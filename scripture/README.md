# Scripture corpus

## Starter corpus

`corpus.json` is a small, retrieved-only starter corpus: 53
passages from the King James Version, which is in the public domain.
Each entry has a reference, the exact text used, and topic tags the
engine uses to find a relevant passage.

The engine never generates Scripture. If a reference is not in this
file, the engine must say "could not retrieve" and must not quote it
from memory.

## Adding a fuller verified Bible

To expand coverage without breaking the integrity rule:

1. Use a verified public-domain text, for example the World English
   Bible (WEB) or a verified KJV edition, from a source you trust.
2. Convert it to the same schema:
   ```json
   {
     "translation": "WEB (public domain)",
     "verses": [
       {"reference": "John 3:16", "text": "...", "topics": ["love", "hope"]}
     ]
   }
   ```
3. Replace `corpus.json`, keeping a backup of the starter file.
4. Run `python3 app.py --verses` and
   `python3 -m unittest discover -s tests -v` to confirm the new file
   loads and the acceptance tests still pass.
5. Update `README.md` with the new translation name and passage count.

Do not paste text you cannot verify into this file and present it as
a verified edition. If you are unsure about a passage, leave it out:
the engine's "could not retrieve" answer is safer than a wrong quotation.
