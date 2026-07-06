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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
