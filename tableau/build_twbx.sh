#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 path/to/workbook.twb [output.twbx]" >&2
  exit 1
fi

workbook_path="$1"
if [[ ! -f "$workbook_path" ]]; then
  echo "Workbook not found: $workbook_path" >&2
  exit 1
fi

if [[ "${workbook_path##*.}" != "twb" ]]; then
  echo "Input must be a .twb workbook: $workbook_path" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
default_output="${workbook_path%.twb}.twbx"
output_path="${2:-$default_output}"
archive_name="$(basename "$output_path")"
staging_dir="$(mktemp -d)"

cleanup() {
  rm -rf "$staging_dir"
}
trap cleanup EXIT

mkdir -p "$staging_dir/Data"
cp "$workbook_path" "$staging_dir/$(basename "$workbook_path")"
find "$repo_root/tableau/data" -maxdepth 1 -type f -exec cp {} "$staging_dir/Data/" \;

(
  cd "$staging_dir"
  zip -qr "$archive_name" .
)

if [[ "$output_path" != /* ]]; then
  mkdir -p "$(dirname "$output_path")"
  mv "$staging_dir/$archive_name" "$PWD/$output_path"
else
  mkdir -p "$(dirname "$output_path")"
  mv "$staging_dir/$archive_name" "$output_path"
fi

echo "Created packaged Tableau workbook: $output_path"
