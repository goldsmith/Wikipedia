# Contributor acknowledgments

Original author: Jonathan Goldsmith. Earlier contributions remain credited in
the Git history and historical changelog.

The proposed 1.5.0 stabilization incorporates Niki's
[#351](https://github.com/goldsmith/Wikipedia/pull/351) unchanged: equality no longer
catches `KeyboardInterrupt` or `SystemExit`. The original author and source commit
`8ccc0f257673534989522d9d07ace25c16b66a87` are preserved in Git history.

Several earlier proposals informed focused changes in this branch. Thank you to:

| Contributor | Proposal | Contribution adapted here |
|---|---|---|
| David Lutz | [#64](https://github.com/goldsmith/Wikipedia/pull/64) | Connection reuse through a Requests session. |
| mkasprz | [#132](https://github.com/goldsmith/Wikipedia/pull/132) | Handling unavailable image URLs. |
| Emmanuel Bizieau | [#137](https://github.com/goldsmith/Wikipedia/pull/137) | Timeouts on API requests. |
| Michael E. Rose | [#157](https://github.com/goldsmith/Wikipedia/pull/157) | Handling absent coordinates. |
| Christopher Beland | [#160](https://github.com/goldsmith/Wikipedia/pull/160) | HTTPS API requests. |
| rowan08 | [#205](https://github.com/goldsmith/Wikipedia/pull/205) | Handling missing collection properties. |
| Anna Katrine Jørgensen | [#219](https://github.com/goldsmith/Wikipedia/pull/219) | Geosearch cache invalidation and absent coordinates. |
| Tim Gates | [#261](https://github.com/goldsmith/Wikipedia/pull/261) | Correcting spelling in documentation. |

These adaptations incorporate the relevant ideas or fixes, rather than every
change in each proposal. The linked discussions retain their original context.
