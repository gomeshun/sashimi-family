# Pending final-family CI configuration

`family-integration.yml.pending` is prepared for the final atomic parent
manifest/gitlink change. It is inactive and has not been run as a GitHub job.
It selects the exact PR head, tests Python 3.11–3.13, builds both artifact forms
without revision injection, executes standard-API numerical smoke outside the
source tree and verifies unrelated-Git sdist rebuilds. Its underlying scripts
have passed the local artifact matrix; that is not execution evidence for this
workflow template.

Do not install this template against the old authoritative component pins.
After F scientific adoption, first verify a complete temporary candidate set;
then apply it with the manifest/gitlinks in one parent migration commit and run
without overrides. Save the exact parent commit and CI evidence. This activates
validation only and contains no publication operation.

The corresponding private-F workflow is now implemented and executed by F PR
#28 (merged source 3a34188347ccc6e795e6fb640f9db1870ff4383b). Its default parent
base is the committed audited-runner input 97101de. Both original/rebuilt checks
pass on Python 3.11–3.13; the fetched CI evidence verifies the exact inputs.
This remains candidate mode. The final dispatch must still pass the SAME final
recorded parent SHA and `family_mode=promoted`, which performs no overrides.
See ../HANDOFF_20260911.md and the merged candidate artifact summary.
