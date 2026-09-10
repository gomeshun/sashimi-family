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

A corresponding private-F workflow draft is kept in its ignored local review
artifacts, because public reports must not copy private implementation/inputs.
Apply it in F before its final artifact build; point its family base at the
parent branch containing the reusable scripts. The final validation dispatch
must use the SAME recorded parent SHA and the workflow's promoted/no-override
mode. Do not confuse candidate-mode success with this required final check.
