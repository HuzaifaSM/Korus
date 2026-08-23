// represents a single changed line between two versions of a file
#[derive(Clone, Debug)]
pub struct LineDiff {
    pub line_number: usize,
    pub prev: Option<String>, // none if line was added
    pub next: Option<String>, // none if line was removed
}

// computes longest common subsequence length table for two line slices
// core of LCS algorithm - 2d dynamic programming table
// where lcs[i][j] = length of LCS prev[0..i] and next[0..j]
fn buildLcsTable(prev: &[&str], next: &[&str]) -> Vec<Vec<usize>> {
    let m = prev.len();
    let n = next.len();
    // initialise a (m+1) x (n + 1) table of zeros
    let mut table = vec![vec![0usize; n + 1]; m + 1];

    for i in 1..=m {
        for j in 1..=n {
            if prev[i - 1] == next[j - 1] {
                // lines match, extend lcs by 1
                table[i][j] = table[i - 1][j - 1] + 1;
            } else {
                // lines differ - take the best of skipping either side
                table[i][j] = table[i - 1][j].max(table[i][j - 1]);
            }
        }
    }

    table
}

// backtracks through lcs to produce diff
// walks from bottom-right corner back to [0][0]
// decides each step whether a line was shared, added or removed
fn backtrack(
    table: &[Vec<usize>],
    prev: &[&str],
    next: &[&str],
    i: usize,
    j: usize,
    diffs: &mut Vec<LineDiff>,
    lineNum: &mut usize,
) {
    if i == 0 && j == 0 {
        return;  // base case - reached 0,0
    }

    if i > 0 && j > 0 && prev[i - 1] == next[j - 1] {
        // lines are the same - recurse and advance both sides
        backtrack(table, prev, next, i - 1, j - 1, diffs, lineNum);
        *lineNum += 1; // shared line - advance line counter
    } else if j > 0 && (i == 0 || table[i][j - 1] >= table[i - 1][j]) {
        // line was added in next
        backtrack(table, prev, next, i, j - 1, diffs, lineNum);
        *lineNum += 1;
        diffs.push(LineDiff {
            line_number: *lineNum,
            prev: None,
            next: Some(next[j - 1].to_string()),
        });
    } else {
        // line removed from prev
        backtrack(table, prev, next, i - 1, j, diffs, lineNum);
        diffs.push(LineDiff {
            line_number: *lineNum + 1,
            prev: Some(prev[i - 1].to_string()),
            next: None,
        });
    }
}

// computes a line-by-line diff using lcs
// insertions and deletions are reported accurately regardless of position
// - inserting a line no longer marks every following line as changed
pub fn diffLines(prev: &str, next: &str) -> Vec<LineDiff> {
    let prevLines: Vec<&str> = prev.lines().collect();
    let nextLines: Vec<&str> = next.lines().collect();

    let table = buildLcsTable(&prevLines, &nextLines);
    let mut diffs = Vec::new();
    let mut lineNum = 0usize;

    backtrack(
        &table,
        &prevLines,
        &nextLines,
        prevLines.len(),
        nextLines.len(),
        &mut diffs,
        &mut lineNum,
    );

    diffs
}
