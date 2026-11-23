#!/bin/sh
# Swap in the approved platform name (and optionally the new web address) across the site.
#
# Usage (from this folder):
#   sh rename-platform.sh "New Platform Name"
#   sh rename-platform.sh "New Platform Name" new-domain.gov.ng
#
# - Replaces every "[Platform Name]" placeholder.
# - Replaces the "[Web address]" placeholder in the data citation.
# - With a domain: also moves nigeriase4all.gov.ng links (incl. apps., data., learning.)
#   to the new domain. Only do this once the new domain actually serves those apps.
# Historical blog titles and event names ("Nigeria SE4ALL Mapathon") are left as published.
set -e
NAME="$1"
DOMAIN="$2"
if [ -z "$NAME" ]; then
  echo 'Usage: sh rename-platform.sh "New Platform Name" [new-domain.gov.ng]' >&2
  exit 1
fi
FILES="index.html about.html accreditation.html blog.html blog-post.html mini-grids.html power-sector.html solar-home-systems.html PRODUCT.md DESIGN.md .impeccable/design.json"
export NAME DOMAIN
for f in $FILES; do
  [ -f "$f" ] || continue
  perl -pi -e 's/\[Platform Name\]/$ENV{NAME}/g' "$f"
  if [ -n "$DOMAIN" ]; then
    perl -pi -e 's/\[Web address\]/https:\/\/$ENV{DOMAIN}/g; s/nigeriase4all\.gov\.ng/$ENV{DOMAIN}/g' "$f"
  fi
done
echo "Renamed to: $NAME${DOMAIN:+ ($DOMAIN)}"
grep -c "\[Platform Name\]" $FILES 2>/dev/null | grep -v ":0" || echo "No placeholders left."
