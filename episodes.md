# Java.in60sec — Episode Log

| # | Topic | Length | Engine module | Video file | Status |
|---|-------|--------|---------------|------------|--------|
| 1 | String Pool: `==` vs `.equals()` | 50 s | `anim.py` | java_string_pool_om.mp4 | Ready |
| 2 | HashMap internals | 53 s | `hm.py` | java_hashmap_om.mp4 | Ready |
| 3 | ArrayList vs LinkedList | 36 s | `al.py` | java_arraylist_vs_linkedlist_om.mp4 | Ready |

## Topic backlog
- `final` vs immutable
- How Garbage Collection works (young/old gen)
- `equals()` & `hashCode()` contract — what breaks if you override only one
- Why `String` is immutable
- `static` explained with memory
- Checked vs unchecked exceptions
- Stack vs Heap: where variables live
- `StringBuilder` vs `+` in a loop
- Java Streams: lazy evaluation
- Threads: race condition on `count++`

---

## Ep 1 — String Pool
**Script (Om, eleven_v4):**
Same text. But Java gives two different answers. [excited] Why?
Let's look inside memory.
When you write a string literal, Java stores it in the String Pool. And "a" just holds its address.
Write the same literal again? Java checks the pool, finds it, and reuses the same object.
So, "a" double-equals "b" is true. Same address!
But "new String" always creates a brand-new object on the heap, with a new address.
That's why "a" double-equals "c" is false. Double-equals only compares references.
Dot equals, on the other hand, compares the actual characters. J. A. V. A. True!
Bonus: intern hands you back the pooled copy, and the old object gets garbage collected.
Remember: double-equals checks the same object. Dot equals checks the same content. Follow for more Java in sixty seconds!

**Caption:**
```
"java" == "java" → true
new String("java") == "java" → false 🤯

Same text. Different answer. Here's why 👇

🔸 String literals live in the String Pool. Java reuses them.
🔸 new String() always creates a fresh object on the heap.
🔸 == compares references (addresses), not content.
🔸 .equals() compares the actual characters.

✅ Rule: Always compare Strings with .equals()

💬 Did this ever bite you in an interview? Comment below!
📌 Save this for your next Java interview
➡️ Follow @java.in60sec for Java in 60 seconds

#java #javaprogramming #javadeveloper #coding #programming #learnjava #javainterview #softwareengineer #codinglife #developer #stringpool #backenddeveloper #techreels #codingreels #100daysofcode
```

## Ep 2 — HashMap internals
Real values used: "apple" hashCode 93029210 → bucket 1, "mango" → 15, "kiwi" → 2, "lemon" → 2 (collision).

**Script:**
How does a HashMap find your value instantly? [excited] Let's look inside.
A HashMap is just an array of buckets. Sixteen, by default.
Put "apple". Java calls hashCode, mixes in the high bits, then does hash AND fifteen. Bucket one! The entry drops straight in.
"Mango"? Bucket fifteen. "Kiwi"? Bucket two.
Now "lemon". Its hash also points to bucket two. That's a collision! Java simply chains it behind kiwi.
When you call get "lemon", Java hashes again, jumps straight to bucket two, and checks equals on each key until it finds lemon. No scanning the whole map. That's O of one, on average.
If one bucket grows past eight entries in a big enough map, it turns into a red-black tree. And once the map is seventy-five percent full, it doubles in size and rehashes.
Remember: hashCode picks the bucket. Equals finds the key. Follow for more Java in sixty seconds!

**Caption:**
```
How does HashMap find your value in ONE jump? ⚡

Here's what happens inside 👇

🔸 HashMap = an array of 16 buckets (by default)
🔸 hashCode() → mix bits → & 15 → bucket index
🔸 Same bucket? Collision → entries get chained
🔸 get() jumps to the bucket, then uses equals() to find the key
🔸 8+ entries in one bucket → becomes a Red-Black Tree
🔸 75% full → table doubles & every entry is rehashed

✅ hashCode() picks the bucket. equals() finds the key.
Override them together. Always.

💬 Which part surprised you most?
📌 Save this, it's a top Java interview question
➡️ Follow @java.in60sec for more

#java #hashmap #javaprogramming #datastructures #javainterview #coding #programming #learnjava #javadeveloper #softwareengineer #backenddeveloper #codinginterview #techreels #codingreels #dsa
```

## Ep 3 — ArrayList vs LinkedList
**Script:**
ArrayList or LinkedList? Most developers pick wrong. [excited] Let's see why.
ArrayList keeps elements side by side in one array. Get index three? It jumps straight there. Instant.
But insert at the front, and every element shifts one step right.
LinkedList is a chain of nodes. Each node points to the next.
Insert at the front? Just relink one pointer. Done.
But get index three? It walks, node by node.
And those nodes are scattered in memory, so the CPU cache hates them.
In real code, ArrayList wins almost every time. Follow for more Java in sixty seconds!

**Caption:**
```
ArrayList or LinkedList? Most devs pick wrong 👀

Let's settle it 👇

📦 ArrayList
✔️ get(i) → O(1), jumps straight to the index
❌ insert at front → O(n), every element shifts

🔗 LinkedList
✔️ insert at front → O(1), just relink a pointer
❌ get(i) → O(n), walks node by node
❌ scattered nodes = CPU cache misses

✅ Verdict: Default to ArrayList. It wins almost every time in real code.

💬 Team ArrayList or Team LinkedList? Comment below 👇
📌 Save for your next interview
➡️ Follow @java.in60sec for more

#java #arraylist #linkedlist #javaprogramming #datastructures #collections #javainterview #coding #programming #learnjava #javadeveloper #softwareengineer #dsa #techreels #codingreels
```
