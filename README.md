# Scanit Scans It

Scanit will scan it, whatever it might be that you want scanned.

## Usage

    $ scanit some-title

This will cause scanit to:

1. Search for scanners
2. Pick the first one it sees
3. Configure it for lineart or grayscale quality coloring
4. Scan a single page to .png
5. Compile the .png into a .pdf, saved as some-title.pdf

You can also pass it multiple page numbers via ``-n``. This will cause scanit to
process multiple pages at the same time, with all scanned pages finally going
into one big PDF at the end.

# License

Scanit is made available under the terms of the GNU General Public License,
version 3.
