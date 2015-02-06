import sys
import re

weasels_filename = "weasels.txt"
irregulars_filename = "irregulars.txt"

def interval_overlap(i1, i2):
  start = max(i1[0], i2[0])
  end = min(i1[1], i2[1])

  if end <= start:
    return None
  else:
    return (start, end)

def highlight_string(string):
  attr = []
  attr.append('31')
  return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def merge_intervals(intervals):
  if len(intervals) < 2:
    return intervals

  intervals.sort()
  result = [intervals[0]]
  for interval in intervals[1:]:
    last_interval = result[-1]
    if last_interval[1] > interval[0]:
      result[-1] = (last_interval[0], max(last_interval[1], interval[1]))
    else:
      result.append(interval)

  return result

def create_weasels_lint():
  with open(weasels_filename) as weasels_file:
    regexes = weasels_file.readlines()

    def weasels_lint(string):
      matches = []
      for regex in regexes:
        ms = re.finditer('\s+(' + regex.strip() + r')(\s+|.|,)', string, re.MULTILINE)
        for m in ms:
          matches.append(m.span(1))
      return matches

    return weasels_lint
  return None

def create_passive_voice_lint():
  with open(irregulars_filename) as irregulars_file:
    regexes = irregulars_file.readlines()

    def passive_voice_lint(string):
      matches = []
      ms = re.finditer(r'\s+((am|are|were|being|is|been|was|be)\s+(\w+ed|'+ r'|'.join(regexes) + r'))(\s+|.|,)', string, re.MULTILINE)
      for m in ms:
        matches.append(m.span(1))
      return matches

    return passive_voice_lint
  return None

def lint(tex_filename, linters):
  with open(tex_filename) as tex_file:
    string = tex_file.read()
    matches = []
    for linter in linters:
      matches = matches + linter(string)

    merged_matches = merge_intervals(matches)
    string_lines = string.split('\n')

    line_start = 0
    for line_number, line in enumerate(string_lines):
      line_end = line_start + len(line) + 1

      # Note: this is not terribly efficient because we are checking all the
      # matches for every line
      line_highlights = []
      for match in merged_matches:
        overlap = interval_overlap((line_start, line_end), (match[0], match[1]))
        if overlap:
          line_highlights.append(overlap)

      highlighted_line = ""
      last_highlight = line_start
      for line_highlight in line_highlights:
        highlighted_line += string[last_highlight:(line_highlight[0])] + highlight_string(string[line_highlight[0]:line_highlight[1]].strip())
        last_highlight = line_highlight[1]

      highlighted_line += string[last_highlight:line_end]

      if line_highlights != []:
        print str(line_number + 1).rjust(5) + " " * 3 + highlighted_line.strip()
      line_start = line_end

def main():
  tex_filenames = sys.argv[1:]
  for tex_filename in tex_filenames:
    lint(tex_filename, [create_weasels_lint(), create_passive_voice_lint()])

if __name__ == "__main__":
  main()
