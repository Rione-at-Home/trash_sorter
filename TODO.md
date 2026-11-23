Fundamental issues
- [ ] Fix authorization issues with uploading to GitHub.
- [ ] Fix v4l2 camera driver not running.

Development Goals
- [ ] Ensure turtle base moves when given gui commands.
- [ ] Ensure camera can detect and categorize garbage according to April tags.
- [ ] Determine default poses for the arm using the gui and poses.py.
- This should include all poses necessary for picking up the various pieces of trash we'll be presented with.
- [ ] Create challenge_node.py containing the state machine for item pickup.
- The challenge node should use either the shuttle or batch strategies; Whichever is more doable (see the issues page of the GitHub repo).
- Personally, since we already have the basket, I think we should go for the batch strategy - James

Stretch Goals
- [ ] New, more formal end effector
- [ ] New, more formal sorting bin