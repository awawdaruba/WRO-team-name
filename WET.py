#!/usr/bin/env python3
import gzip
from warcio.archiveiterator import ArchiveIterator
import html2text

INPUT    = 'jarrar-site.warc.gz'
OUTPUT   = 'jarrar-site.wet.gz'

# html2text will turn HTML → Markdown‑style plain text
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True

with gzip.open(INPUT,  'rb') as stream, \
     gzip.open(OUTPUT, 'wt', encoding='utf-8') as out:

    for record in ArchiveIterator(stream):
        # only process real HTTP responses
        if record.rec_type != 'response':
            continue

        # grab the request URI so WET knows where it came from
        uri = record.rec_headers.get_header('WARC-Target-URI')
        http_ct = record.http_headers and record.http_headers.get_header('Content-Type') or ''

        # only extract from HTML payloads
        if 'text/html' in http_ct:
            raw   = record.content_stream().read()
            try:
                html = raw.decode('utf-8', errors='ignore')
            except:
                html = raw.decode('latin1', errors='ignore')

            text = converter.handle(html)
            btxt = text.encode('utf-8')

            # write a minimal WET‑style header
            out.write('WARC/1.0\n')
            out.write('WARC-Type: conversion\n')
            out.write(f'WARC-Target-URI: {uri}\n')
            out.write('Content-Type: text/plain\n')
            out.write(f'Content-Length: {len(btxt)}\n')
            out.write('\n')
            out.write(text)
            out.write('\n\n')
