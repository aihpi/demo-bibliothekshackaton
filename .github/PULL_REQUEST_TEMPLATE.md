**Issue:** #___

**Description:**
(Replace this with why the change was needed and how it works. Mention anything a reviewer should watch out for: trade-offs, known debt, new packages, edge cases.)

---------- remove this line and everything below from the squashed commit message ----------

### Other info

(Optional. Screenshots, open questions, follow-up ideas.)

### Before requesting review

- [ ] The PR title follows the rules below
- [ ] The issue number and description above are filled in
- [ ] The code is easy to follow: self-explanatory, or commented where it isn't
- [ ] Tests are added, updated or removed as needed
- [ ] `pytest` passes and `ruff check` and `ruff format --check` are clean
- [ ] I skimmed the diff on GitHub

### Before squash merging

- [ ] The commit title still follows the rules below. Keep the PR number GitHub adds in parentheses at the end.
- [ ] The commit body contains only the Issue and Description sections above. GitHub fills it with the list of commits by default, so replace that.
- [ ] If the PR targets a feature branch, close the issue by hand after merging. Closing keywords like `Closes #12` only work for PRs into `main`.

### Title rules

The PR title becomes the squashed commit title, so it ends up in the git history for good.

- Written like a title: capital letter, imperative verb, no full stop
- Prefixed with `#` and the **issue** number, not the PR number
- Can be a bit longer than a normal commit title if the PR does several things

Example: `#3 Move the azure class to its own bundle and refactor the interface`
