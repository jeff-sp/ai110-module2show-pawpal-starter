# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
A user should be able to add a pet, schedule a walk, and see today's tasks.
One Owner has 1 or many Pets.
Owner requests plan from Scheduler.
Scheduler reads constraints from Owner.
Scheduler reads Pet; Scheduler looks at a Pet's data to build the plan but does not own or store the Pet.
Scheduler plans Tasks.
0 or many Tasks belong to each Pet.
- What classes did you include, and what responsibilities did you assign to each?
There should be four classes: Scheduler, Owner, Pet, and Task.
Scheduler behaviors:
    - generates a schedule when given an owner, pet, and tasks, returned a list of Tasks.
    - explain plan: input a list of Tasks and return a string.
Owner has a (string) name, (integer) available_time_minutes, (dictionary) preferences, and (list of type Pet) pets.
Owner behavior:
    - add_pet given input Pet (return None), append to list of Pets
Pet has (string) name and (string) species.
Task has (string) title, (integer) durtaion_in_minutes, and (integer) priority.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
