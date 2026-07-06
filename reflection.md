# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The user should be able to add a pet, schedule their tasks, and availability
- What classes did you include, and what responsibilities did you assign to each?
 - Owner: Holds the owner's info and available time. Can add pets and set availability.
 - Pet:Holds a pet's details and its list of tasks. Can add and remove tasks.
 - Task: Holds one care task (type, duration, priority). Knows if it fits in the available time.
 - Scheduler: Reads the owner's time and the pets' tasks, then builds and explains the daily plan.
 - TaskType and Time: TaskType lists the task categories; Time handles time math.

**b. Design changes**

- Did your design change during implementation? 
- If yes, describe at least one change and why you made it.

The Time class was added to the UML along with it relationships. The Owner and Task relied on it however it wasn't present and would cause the diagram and code to be out of sync. T

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

It considers the owner's available hours, fixed appointment times (like "meds at 09:00"), task priority, task duration, and whether a task is already done.

- How did you decide which constraints mattered most?

Fixed times come first because they have to happen at a set time. After that I sort by priority so the important tasks get a slot before optional ones, and use duration only to break ties. A pet owner cares most that the essential care gets done.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

It places each task in the first open slot that fits instead of searching for the best possible fit. So one long task can take up space that two shorter tasks could have used, and anything that doesn't fit is skipped.

- Why is that tradeoff reasonable for this scenario?

For one owner's short daily list, a perfect schedule isn't worth the extra complexity. The simple approach is fast and easy to follow, and skipped tasks are shown with a reason so nothing disappears silently.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I mostly used AI as a second set of eyes. It looked over my code and told me which behaviors were worth testing, helped me write the test functions for sorting, recurrence, and conflicts, and checked if my UML still matched my code. I also had it help clean up the Streamlit display and the README.

- What kinds of prompts or questions were most helpful?

Specific questions worked way better than open-ended ones. When I asked something exact like "does my UML still match my code" or "what edge cases matter for a scheduler like this," I got a real answer back. When I asked something vague I just got a vague answer.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When I had it check my UML, it turned out my old diagram listed methods like fitsWithin and canFit that I never actually built. I didn't just leave them there, I got the diagram fixed so it matched the real code. I also kept my own naming style instead of changing everything just because it suggested it.

- How did you evaluate or verify what the AI suggested?

I didn't assume the tests worked just because they were written and ran pytest myself and watched all 6 pass. or the sample output in the README, I actually ran main.py and copied the real output instead of making one up.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I tested three things, that tasks come back sorted by time even when I add them out of order, that finishing a daily task makes a new one for the next day, and that two tasks at the same time get flagged as a conflict. I also added one more test to make sure tasks that are just back-to-back don't get flagged.

- Why were these tests important?

These are the parts the whole scheduler leans on. Sorting and recurrence are easy to get a little wrong without noticing, especially the dates. And the back-to-back one matters because it's easy to accidentally flag tasks that only touch but don't really overlap.

**b. Confidence**

- How confident are you that your scheduler works correctly?

Around 4 out of 5. The three riskiest behaviors are tested and passing and the main logic is clean. I'm not saying 5 because there are still paths I haven't tested, so I can't fully promise they all work.

- What edge cases would you test next if you had more time?

A pet with no tasks or no availability set, a fixed task that starts inside the window but ends after it, priority ties that come down to duration, and recurrence rolling over a month, a year, or a leap day like Feb 28.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm happiest with how the scheduling logic came together as one thing. Fixed tasks lock in first, the flexible ones fill the gaps by priority, and anything that gets skipped shows a reason so it doesn't just vanish. Getting the tests passing and the UML matching the code again made it feel actually done, not just working.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd make the placement smarter so it doesn't just grab the first slot that fits. Right now a long task can eat space that two short ones could have used. I'd also add the edge-case tests I mentioned, and let people edit or delete tasks in the app instead of only adding them.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Keeping the design and the code in sync really matters. My UML slowly drifted from the code as I added stuff, and it would have been misleading if I never checked. And AI is great for reviewing and drafting, but I still have to check its work myself, run the tests, run the app, and make sure it's actually real before I trust it.
