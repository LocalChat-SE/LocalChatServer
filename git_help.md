1. Download some git software.
Assuming you’re on windows, you can either get a GUI program, like this one:
https://desktop.github.com

Or you can get just the command interface:
https://git-scm.com/download/win

2. Create a github account. Sign in on the software linked above and send me your username.

The GUI sign in should be straightforward. 
Alternatively, to sign in on the command interface (if you choose to use it), check out some stack overflow posts on ‘git config --global’ and I recommend the credential helper.

3. Clone the repository.vThere is a green button on the upper right side of the page that says ‘Clone or Download’. Copy the .git web url from that pop-up. From the GUI, there should be an option somewhere to add a repository- from there you can paste that repository url.

If you use the command interface, type 
‘git clone [URL]’

This makes a clone of the repository on your computer

If you make edits to the code, they should appear in the GUI. When you are done making changes, then ‘commit’ them with a description of your changes. I think of a commit as making a statement that you are committed to your set of edits and are ready to save them. 

To commit, you choose which files you want to include in the commit by staging them. When you commit, everything that has been staged will be added to the commit. 

Now that new commit is on your computer, but it hasn’t been logged at the origin, where the code is hosted on GitHub. No-one else can see it yet. You have to ‘push’ the code to update Github.

If you’re using the command interface, then the following commands are used:

See what files are changed and staged:
git status

Stage all changes:
git add .

Commit the staged changes:
git commit -m “helpful description”

Update the origin:
git push

