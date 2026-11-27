# Commercial closeout — 30 tasks

Status is evidence-based; implemented does not mean deployed.
1. Check latest account CI — verified at 5dd0ae1.
2. Check frontend build — verified at 5dd0ae1.
3. Check private transport CI — verified at 5dd0ae1.
4. Check current safety audit — verified at 5dd0ae1.
5. Check SHOA window CI — pending.
6. Test maintenance disabled gate — verified at 5dd0ae1.
7. Test maintenance production rejection — verified at 5dd0ae1.
8. Test sandbox maintenance invocation — verified at 5dd0ae1.
9. Verify password rotation tests. — verified at 5dd0ae1.
10. Verify reset token invalidation. — verified at 5dd0ae1.
11. Test terms missing file. — verified at 5dd0ae1.
12. Test terms mismatched digest. — verified at 5dd0ae1.
13. Test terms oversized document. — verified at 5dd0ae1.
14. Test terms invalid UTF-8. — verified at 5dd0ae1.
15. Verify terms API response contract. — verified at 5dd0ae1.
16. Verify deletion API response contract. — verified at 5dd0ae1.
17. Test rejected deletion resubmission policy.
18. Validate admin isolation. — verified at 5dd0ae1.
19. Validate aggregate metrics with fixtures. — verified at 5dd0ae1.
20. Select maintained MFA library and review compatibility.
21. Implement MFA enrollment and verification.
22. Test MFA replay and revocation.
23. Verify commercial frontend with preview flags enabled.
24. Test mobile account flow.
25. Verify authoritative payment contract.
26. Validate sandbox checkout and webhook.
27. Provision isolated database only with cost approval.
28. Verify backup and restore.
29. Approve final legal text and publish exact digest.
30. Complete release acceptance and obtain launch approval.

No real charges, paid infrastructure or production deployment are authorized by this checklist.

Evidence 2026-11-27: commit 5dd0ae1133627a816414c3e0c653598094f41f6f; accounts run 45998569718 job 140504088968 (75 tests, success); frontend 45998569850, transport 45998569730, safety 45998569812 success. SHOA run 45998569802 in progress. Task 19 covers trial metric deltas; payment metric fixtures still needed before broader dashboard acceptance. No production changes.
