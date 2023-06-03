#!/bin/bash -xe
IN_FILE='/Users/saggese/Downloads/Tools\ -\ PyCharm.docx'
OUT_PREFIX="docs/Tools-PyCharm"
OUT_FILE="${OUT_PREFIX}.md"
OUT_FIGS="${OUT_PREFIX}_figs"

# Convert.
rm -rf $OUT_FIGS
cmd="pandoc --extract-media $OUT_FIGS -f docx -t markdown -o $OUT_FILE $IN_FILE"
eval $cmd

# Move the media.
mv $OUT_FIGS/{media/*,}
rm -rf $OUT_FIGS/media

# Clean up.
# \_ -> _
perl -pi -e "s/\\\_/_/g" $OUT_FILE

# \@ -> @
perl -pi -e "s/\\\@/@/g" $OUT_FILE

# -\> -> ->
perl -pi -e "s/-\>/->/g" $OUT_FILE

# Let\'s -> Let's
perl -pi -e "s/\\'/\'/g" $OUT_FILE

# \| -> |
perl -pi -e "s/\\|/\|/g" $OUT_FILE
#
# \$ -> $
perl -pi -e 's/\\\$/\$/g' $OUT_FILE

#perl -pi -e 's/\s*```{=html}\n\s*<!-- -->\n\s*```/mg' $OUT_FILE

SCRIPT_NAME="/tmp/replace.py"
cat <<EOF >$SCRIPT_NAME
#! /usr/bin/env python

import re
import sys

filename = sys.argv[1]
# Read the entire file.
with open(filename, 'r') as file:
    lines = file.readlines()
lines = "\n".join(lines)

regex = r"\s*```{=html}\n\s*<!-- -->\n\s*```"

subst = ""

# You can manually specify the number of replacements by changing the 4th argument
result = re.sub(regex, subst, lines, 1, re.MULTILINE)

# Write the modified content back to the file
lines = lines.split("\n")
with open(filename, 'w') as file:
file.write(lines)
EOF
chmod +x $SCRIPT_NAME


# "# \# Running PyCharm remotely" -> "# Running PyCharm remotely"
perl -pi -e "s/\\\#+ //g" $OUT_FILE

# \`nid\` -> `nid`
perl -pi -e "s/\\\\\`(.*?)\\\\\`/\`\1\`/g" $OUT_FILE

#
perl -pi -e "s|$OUT_FIGS/media|$OUT_FIGS|g" $OUT_FILE
