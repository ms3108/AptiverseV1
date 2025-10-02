"""
Database seeding script for questions and badges
Run this script to populate the database with initial data
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import json

def seed_badges(db: Session):
    """Create initial badge definitions"""
    badges_data = [
        {
            "name": "First Steps",
            "description": "Solve your first question",
            "icon": "🎯",
            "criteria": json.dumps({"total_questions": 1})
        },
        {
            "name": "Getting Started",
            "description": "Solve 10 questions",
            "icon": "🌟",
            "criteria": json.dumps({"total_questions": 10})
        },
        {
            "name": "Half Century",
            "description": "Solve 50 questions",
            "icon": "💯",
            "criteria": json.dumps({"total_questions": 50})
        },
        {
            "name": "Centurion",
            "description": "Solve 100 questions",
            "icon": "🏆",
            "criteria": json.dumps({"total_questions": 100})
        },
        {
            "name": "On Fire",
            "description": "Maintain a 7-day streak",
            "icon": "🔥",
            "criteria": json.dumps({"current_streak": 7})
        },
        {
            "name": "Consistent Learner",
            "description": "Maintain a 30-day streak",
            "icon": "⚡",
            "criteria": json.dumps({"current_streak": 30})
        },
        {
            "name": "Streak Master",
            "description": "Maintain a 100-day streak",
            "icon": "🎖️",
            "criteria": json.dumps({"current_streak": 100})
        },
        {
            "name": "Level 5",
            "description": "Reach Level 5",
            "icon": "🥉",
            "criteria": json.dumps({"level": 5})
        },
        {
            "name": "Level 10",
            "description": "Reach Level 10",
            "icon": "🥈",
            "criteria": json.dumps({"level": 10})
        },
        {
            "name": "Level 20",
            "description": "Reach Level 20",
            "icon": "🥇",
            "criteria": json.dumps({"level": 20})
        },
        {
            "name": "XP Hunter",
            "description": "Earn 1000 XP",
            "icon": "💎",
            "criteria": json.dumps({"xp": 1000})
        },
        {
            "name": "XP Master",
            "description": "Earn 5000 XP",
            "icon": "💠",
            "criteria": json.dumps({"xp": 5000})
        }
    ]
    
    for badge_data in badges_data:
        # Check if badge already exists
        existing = db.query(models.Badge).filter(models.Badge.name == badge_data["name"]).first()
        if not existing:
            badge = models.Badge(**badge_data)
            db.add(badge)
            print(f"✅ Created badge: {badge_data['name']}")
        else:
            print(f"⏭️  Badge already exists: {badge_data['name']}")
    
    db.commit()
    print(f"\n✅ Badge seeding complete!")


def seed_questions(db: Session):
    """Create initial question bank with aptitude MCQs"""
    questions_data = [
        # Quantitative Aptitude - Numbers
        {
            "title": "Average of Numbers",
            "description": "The average of 5 consecutive odd numbers is 27. What is the largest number?",
            "difficulty": "Easy",
            "topic": "Averages",
            "option_a": "29",
            "option_b": "31",
            "option_c": "33",
            "option_d": "35",
            "correct_answer": "B",
            "explanation": "If average is 27, middle number is 27. For 5 consecutive odd numbers: 23, 25, 27, 29, 31. Largest is 31.",
            "xp_reward": 10
        },
        {
            "title": "Percentage Calculation",
            "description": "A shopkeeper marks his goods 40% above cost price but allows a discount of 20%. What is his profit percentage?",
            "difficulty": "Medium",
            "topic": "Percentages",
            "option_a": "10%",
            "option_b": "12%",
            "option_c": "15%",
            "option_d": "20%",
            "correct_answer": "B",
            "explanation": "Let CP = 100. Marked Price = 140. After 20% discount: 140 × 0.8 = 112. Profit = 12%.",
            "xp_reward": 15
        },
        {
            "title": "Maximum Subarray Sum",
            "description": "Find the contiguous subarray which has the largest sum and return its sum.",
            "difficulty": "Medium",
            "topic": "Arrays",
            "option_a": "Brute force (O(n³))",
            "option_b": "Kadane's Algorithm (O(n))",
            "option_c": "Divide and Conquer (O(n log n))",
            "option_d": "Dynamic Programming (O(n²))",
            "correct_answer": "B",
            "explanation": "Kadane's Algorithm is optimal with O(n) time and O(1) space complexity.",
            "xp_reward": 15
        },
        {
            "title": "Longest Substring Without Repeating Characters",
            "description": "Given a string s, find the length of the longest substring without repeating characters.",
            "difficulty": "Medium",
            "topic": "Strings",
            "option_a": "Brute force with nested loops",
            "option_b": "Sliding window with hash set",
            "option_c": "Dynamic programming",
            "option_d": "Recursion with memoization",
            "correct_answer": "B",
            "explanation": "Sliding window with hash set achieves O(n) time complexity efficiently.",
            "xp_reward": 15
        },
        {
            "title": "Trapping Rain Water",
            "description": "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
            "difficulty": "Hard",
            "topic": "Arrays",
            "option_a": "Brute force (compute left/right max for each position)",
            "option_b": "Precompute left/right max arrays",
            "option_c": "Two pointers",
            "option_d": "Both B and C",
            "correct_answer": "D",
            "explanation": "Both approaches work. Two pointers is most space-efficient with O(1) extra space.",
            "xp_reward": 20
        },
        
        # Linked Lists
        {
            "title": "Reverse Linked List",
            "description": "Given the head of a singly linked list, reverse the list and return the reversed list.",
            "difficulty": "Easy",
            "topic": "Linked Lists",
            "option_a": "Iterative approach with 3 pointers",
            "option_b": "Recursive approach",
            "option_c": "Use stack",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All approaches work. Iterative is most efficient with O(1) space (recursive uses O(n) stack space).",
            "xp_reward": 10
        },
        {
            "title": "Detect Cycle in Linked List",
            "description": "Given head of a linked list, determine if it has a cycle in it.",
            "difficulty": "Easy",
            "topic": "Linked Lists",
            "option_a": "Use hash set to track visited nodes",
            "option_b": "Floyd's Cycle Detection (slow/fast pointers)",
            "option_c": "Modify node values",
            "option_d": "Both A and B",
            "correct_answer": "D",
            "explanation": "Both work. Floyd's algorithm is more space-efficient with O(1) space vs O(n) for hash set.",
            "xp_reward": 10
        },
        {
            "title": "Merge Two Sorted Lists",
            "description": "Merge two sorted linked lists and return it as a sorted list.",
            "difficulty": "Easy",
            "topic": "Linked Lists",
            "option_a": "Iterative merge",
            "option_b": "Recursive merge",
            "option_c": "Convert to arrays, merge, then convert back",
            "option_d": "Both A and B",
            "correct_answer": "D",
            "explanation": "Both iterative and recursive approaches work efficiently in O(m+n) time.",
            "xp_reward": 10
        },
        
        # Trees
        {
            "title": "Binary Tree Traversal",
            "description": "What is the order of nodes visited in Inorder traversal of a binary tree?",
            "difficulty": "Easy",
            "topic": "Trees",
            "option_a": "Root, Left, Right",
            "option_b": "Left, Root, Right",
            "option_c": "Left, Right, Root",
            "option_d": "Root, Right, Left",
            "correct_answer": "B",
            "explanation": "Inorder traversal visits nodes in order: Left subtree → Root → Right subtree.",
            "xp_reward": 10
        },
        {
            "title": "Maximum Depth of Binary Tree",
            "description": "Find the maximum depth of a binary tree (number of nodes along the longest path from root to leaf).",
            "difficulty": "Easy",
            "topic": "Trees",
            "option_a": "Recursive DFS",
            "option_b": "Iterative BFS",
            "option_c": "Iterative DFS with stack",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All three approaches work. Recursive DFS is most concise.",
            "xp_reward": 10
        },
        {
            "title": "Validate Binary Search Tree",
            "description": "Determine if a binary tree is a valid binary search tree (BST).",
            "difficulty": "Medium",
            "topic": "Trees",
            "option_a": "Check each node against its parent only",
            "option_b": "Inorder traversal should be sorted",
            "option_c": "Pass valid range (min, max) in recursion",
            "option_d": "Both B and C",
            "correct_answer": "D",
            "explanation": "Both approaches work. Range-checking is more direct; inorder traversal is elegant.",
            "xp_reward": 15
        },
        {
            "title": "Lowest Common Ancestor",
            "description": "Find the lowest common ancestor (LCA) of two nodes in a binary tree.",
            "difficulty": "Medium",
            "topic": "Trees",
            "option_a": "Store paths from root to both nodes, find divergence",
            "option_b": "Recursive approach checking left/right subtrees",
            "option_c": "Use parent pointers",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All approaches work. Recursive approach is most elegant with O(n) time, O(h) space.",
            "xp_reward": 15
        },
        
        # Graphs
        {
            "title": "Graph Representation",
            "description": "Which data structure is best for representing a sparse graph?",
            "difficulty": "Easy",
            "topic": "Graphs",
            "option_a": "Adjacency Matrix",
            "option_b": "Adjacency List",
            "option_c": "Edge List",
            "option_d": "Incidence Matrix",
            "correct_answer": "B",
            "explanation": "Adjacency list is space-efficient for sparse graphs: O(V+E) vs O(V²) for matrix.",
            "xp_reward": 10
        },
        {
            "title": "Detect Cycle in Undirected Graph",
            "description": "How to detect a cycle in an undirected graph?",
            "difficulty": "Medium",
            "topic": "Graphs",
            "option_a": "DFS with parent tracking",
            "option_b": "Union-Find (Disjoint Set)",
            "option_c": "BFS with visited set",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All approaches work. Union-Find is efficient for multiple queries.",
            "xp_reward": 15
        },
        {
            "title": "Shortest Path in Unweighted Graph",
            "description": "What algorithm finds shortest path in an unweighted graph?",
            "difficulty": "Easy",
            "topic": "Graphs",
            "option_a": "Breadth-First Search (BFS)",
            "option_b": "Depth-First Search (DFS)",
            "option_c": "Dijkstra's Algorithm",
            "option_d": "Bellman-Ford Algorithm",
            "correct_answer": "A",
            "explanation": "BFS guarantees shortest path in unweighted graphs with O(V+E) complexity.",
            "xp_reward": 10
        },
        {
            "title": "Topological Sort",
            "description": "Topological sorting is possible only for which type of graph?",
            "difficulty": "Medium",
            "topic": "Graphs",
            "option_a": "Directed Acyclic Graph (DAG)",
            "option_b": "Undirected Graph",
            "option_c": "Cyclic Graph",
            "option_d": "Complete Graph",
            "correct_answer": "A",
            "explanation": "Topological sort only works on DAGs (graphs with no cycles).",
            "xp_reward": 15
        },
        
        # Dynamic Programming
        {
            "title": "Fibonacci Number",
            "description": "What is the optimal time complexity for computing nth Fibonacci number?",
            "difficulty": "Easy",
            "topic": "Dynamic Programming",
            "option_a": "O(2^n) - Naive recursion",
            "option_b": "O(n) - DP with memoization",
            "option_c": "O(log n) - Matrix exponentiation",
            "option_d": "O(1) - Direct formula",
            "correct_answer": "D",
            "explanation": "Binet's formula computes Fibonacci in O(1), though O(n) DP is more practical.",
            "xp_reward": 10
        },
        {
            "title": "Coin Change Problem",
            "description": "Given coins of different denominations and a total amount, find the minimum number of coins needed. What approach works?",
            "difficulty": "Medium",
            "topic": "Dynamic Programming",
            "option_a": "Greedy approach",
            "option_b": "Dynamic Programming",
            "option_c": "Backtracking",
            "option_d": "Both B and C",
            "correct_answer": "D",
            "explanation": "DP is optimal (O(amount × n)). Greedy doesn't always work (e.g., coins [1,3,4], amount 6).",
            "xp_reward": 15
        },
        {
            "title": "Longest Common Subsequence",
            "description": "Find the length of longest common subsequence (LCS) between two strings. What's the time complexity of DP solution?",
            "difficulty": "Medium",
            "topic": "Dynamic Programming",
            "option_a": "O(n)",
            "option_b": "O(n log n)",
            "option_c": "O(n²)",
            "option_d": "O(2^n)",
            "correct_answer": "C",
            "explanation": "DP solution uses 2D table with O(m×n) time and space complexity.",
            "xp_reward": 15
        },
        {
            "title": "0/1 Knapsack",
            "description": "In 0/1 Knapsack problem, what does 0/1 signify?",
            "difficulty": "Medium",
            "topic": "Dynamic Programming",
            "option_a": "Items are binary (0 or 1)",
            "option_b": "Each item can be taken 0 or 1 times",
            "option_c": "Weights are 0 or 1",
            "option_d": "Values are 0 or 1",
            "correct_answer": "B",
            "explanation": "0/1 means each item can be either taken (1) or not taken (0), no fractions allowed.",
            "xp_reward": 15
        },
        
        # Sorting & Searching
        {
            "title": "Binary Search Complexity",
            "description": "What is the time complexity of binary search on a sorted array?",
            "difficulty": "Easy",
            "topic": "Searching",
            "option_a": "O(n)",
            "option_b": "O(log n)",
            "option_c": "O(n log n)",
            "option_d": "O(1)",
            "correct_answer": "B",
            "explanation": "Binary search halves the search space each iteration, giving O(log n) complexity.",
            "xp_reward": 10
        },
        {
            "title": "QuickSort Average Case",
            "description": "What is the average-case time complexity of QuickSort?",
            "difficulty": "Easy",
            "topic": "Sorting",
            "option_a": "O(n)",
            "option_b": "O(n log n)",
            "option_c": "O(n²)",
            "option_d": "O(log n)",
            "correct_answer": "B",
            "explanation": "QuickSort averages O(n log n), though worst case is O(n²) with bad pivots.",
            "xp_reward": 10
        },
        {
            "title": "Merge Sort Space Complexity",
            "description": "What is the space complexity of Merge Sort?",
            "difficulty": "Medium",
            "topic": "Sorting",
            "option_a": "O(1)",
            "option_b": "O(log n)",
            "option_c": "O(n)",
            "option_d": "O(n²)",
            "correct_answer": "C",
            "explanation": "Merge Sort requires O(n) auxiliary space for merging subarrays.",
            "xp_reward": 15
        },
        {
            "title": "Find Peak Element",
            "description": "A peak element is greater than its neighbors. Can we find a peak in O(log n) time?",
            "difficulty": "Medium",
            "topic": "Searching",
            "option_a": "No, must check all elements",
            "option_b": "Yes, using binary search",
            "option_c": "Yes, but only if array is sorted",
            "option_d": "Only with randomized algorithm",
            "correct_answer": "B",
            "explanation": "Binary search works: move towards the increasing slope to find a peak in O(log n).",
            "xp_reward": 15
        },
        
        # Stack & Queue
        {
            "title": "Valid Parentheses",
            "description": "Check if a string of brackets is valid (properly opened and closed). What data structure is best?",
            "difficulty": "Easy",
            "topic": "Stack",
            "option_a": "Array",
            "option_b": "Stack",
            "option_c": "Queue",
            "option_d": "Hash Map",
            "correct_answer": "B",
            "explanation": "Stack is perfect: push opening brackets, pop and match closing brackets.",
            "xp_reward": 10
        },
        {
            "title": "Implement Queue Using Stacks",
            "description": "Can you implement a queue using two stacks?",
            "difficulty": "Medium",
            "topic": "Queue",
            "option_a": "No, impossible",
            "option_b": "Yes, with amortized O(1) operations",
            "option_c": "Yes, but all operations become O(n)",
            "option_d": "Only if stacks are unbounded",
            "correct_answer": "B",
            "explanation": "Use two stacks: one for enqueue, one for dequeue. Amortized O(1) per operation.",
            "xp_reward": 15
        },
        {
            "title": "Min Stack",
            "description": "Design a stack that supports push, pop, top, and retrieving minimum element in O(1) time.",
            "difficulty": "Medium",
            "topic": "Stack",
            "option_a": "Use two stacks (one for elements, one for mins)",
            "option_b": "Store min with each element",
            "option_c": "Use auxiliary variable",
            "option_d": "Both A and B",
            "correct_answer": "D",
            "explanation": "Both approaches achieve O(1) operations. Two-stack approach is most intuitive.",
            "xp_reward": 15
        },
        
        # Heap & Priority Queue
        {
            "title": "Heap Property",
            "description": "In a max heap, what is true about every node?",
            "difficulty": "Easy",
            "topic": "Heap",
            "option_a": "It's greater than its children",
            "option_b": "It's smaller than its children",
            "option_c": "It's equal to its children",
            "option_d": "No specific relation",
            "correct_answer": "A",
            "explanation": "Max heap property: parent ≥ children. Min heap is opposite: parent ≤ children.",
            "xp_reward": 10
        },
        {
            "title": "Kth Largest Element",
            "description": "Find the kth largest element in an unsorted array. What's an efficient approach?",
            "difficulty": "Medium",
            "topic": "Heap",
            "option_a": "Sort array then access k-1 index: O(n log n)",
            "option_b": "Use min heap of size k: O(n log k)",
            "option_c": "QuickSelect algorithm: O(n) average",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All work. QuickSelect is optimal (O(n) average), min heap is good for streams.",
            "xp_reward": 15
        },
        
        # Bit Manipulation
        {
            "title": "Count Set Bits",
            "description": "Count the number of 1's in binary representation of an integer. What's an efficient approach?",
            "difficulty": "Easy",
            "topic": "Bit Manipulation",
            "option_a": "Check each bit with right shift: O(log n)",
            "option_b": "Use Brian Kernighan's algorithm: O(k) where k = set bits",
            "option_c": "Precompute lookup table: O(1)",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All work. Brian Kernighan's (n & n-1) is elegant and efficient.",
            "xp_reward": 10
        },
        {
            "title": "Single Number",
            "description": "Every element appears twice except one. Find the single one in O(n) time and O(1) space.",
            "difficulty": "Easy",
            "topic": "Bit Manipulation",
            "option_a": "Use hash map",
            "option_b": "Sort array",
            "option_c": "XOR all elements",
            "option_d": "Use two pointers",
            "correct_answer": "C",
            "explanation": "XOR all elements: duplicates cancel out (a ⊕ a = 0), leaving the single number.",
            "xp_reward": 10
        },
        
        # Greedy
        {
            "title": "Activity Selection",
            "description": "Select maximum number of non-overlapping activities. What strategy works?",
            "difficulty": "Medium",
            "topic": "Greedy",
            "option_a": "Sort by start time",
            "option_b": "Sort by end time",
            "option_c": "Sort by duration",
            "option_d": "Dynamic Programming",
            "correct_answer": "B",
            "explanation": "Greedy approach: sort by end time, always pick earliest finishing activity.",
            "xp_reward": 15
        },
        {
            "title": "Jump Game",
            "description": "Given an array where each element is max jump length from that position, can you reach the last index?",
            "difficulty": "Medium",
            "topic": "Greedy",
            "option_a": "Greedy: track max reachable index",
            "option_b": "Dynamic Programming",
            "option_c": "Backtracking",
            "option_d": "All of the above",
            "correct_answer": "D",
            "explanation": "All work. Greedy is most efficient: O(n) time, O(1) space.",
            "xp_reward": 15
        },
        
        # Backtracking
        {
            "title": "N-Queens Problem",
            "description": "Place N queens on N×N chessboard such that no two queens attack each other. What approach is used?",
            "difficulty": "Hard",
            "topic": "Backtracking",
            "option_a": "Greedy",
            "option_b": "Dynamic Programming",
            "option_c": "Backtracking",
            "option_d": "Divide and Conquer",
            "correct_answer": "C",
            "explanation": "Backtracking is needed to explore all valid placements and backtrack on conflicts.",
            "xp_reward": 20
        },
        {
            "title": "Sudoku Solver",
            "description": "What is the time complexity of backtracking solution for Sudoku?",
            "difficulty": "Hard",
            "topic": "Backtracking",
            "option_a": "O(n²)",
            "option_b": "O(9^(n²))",
            "option_c": "O(n!)",
            "option_d": "O(2^n)",
            "correct_answer": "B",
            "explanation": "Worst case tries 9 possibilities for each cell, giving O(9^(n²)) where n=9.",
            "xp_reward": 20
        },
        
        # Hash Tables
        {
            "title": "Hash Collision Resolution",
            "description": "Which is NOT a collision resolution technique in hash tables?",
            "difficulty": "Easy",
            "topic": "Hashing",
            "option_a": "Chaining",
            "option_b": "Open Addressing",
            "option_c": "Linear Probing",
            "option_d": "Binary Search",
            "correct_answer": "D",
            "explanation": "Binary search is not used for hash collision. Common methods: chaining, open addressing, linear/quadratic probing.",
            "xp_reward": 10
        },
        {
            "title": "HashMap Time Complexity",
            "description": "What is the average-case time complexity for insert/search/delete in a well-designed hash table?",
            "difficulty": "Easy",
            "topic": "Hashing",
            "option_a": "O(1)",
            "option_b": "O(log n)",
            "option_c": "O(n)",
            "option_d": "O(n log n)",
            "correct_answer": "A",
            "explanation": "Hash tables provide O(1) average-case operations (worst case O(n) with many collisions).",
            "xp_reward": 10
        },
        
        # Sliding Window
        {
            "title": "Maximum Sum Subarray of Size K",
            "description": "Find maximum sum of any contiguous subarray of size k. What's the optimal approach?",
            "difficulty": "Medium",
            "topic": "Sliding Window",
            "option_a": "Brute force: O(n×k)",
            "option_b": "Sliding window: O(n)",
            "option_c": "Dynamic Programming: O(n²)",
            "option_d": "Divide and Conquer: O(n log n)",
            "correct_answer": "B",
            "explanation": "Sliding window maintains sum by adding new element and removing leftmost: O(n).",
            "xp_reward": 15
        },
        
        # Two Pointers
        {
            "title": "Container With Most Water",
            "description": "Given heights array, find two lines that form a container holding maximum water. What approach works?",
            "difficulty": "Medium",
            "topic": "Two Pointers",
            "option_a": "Brute force: O(n²)",
            "option_b": "Two pointers from ends: O(n)",
            "option_c": "Dynamic Programming: O(n²)",
            "option_d": "Greedy with sorting: O(n log n)",
            "correct_answer": "B",
            "explanation": "Two pointers: start from ends, move pointer with smaller height inward.",
            "xp_reward": 15
        },
        
        # Matrix
        {
            "title": "Rotate Matrix 90 Degrees",
            "description": "Rotate an n×n matrix 90 degrees clockwise in-place. What's the approach?",
            "difficulty": "Medium",
            "topic": "Matrix",
            "option_a": "Transpose then reverse rows",
            "option_b": "Transpose then reverse columns",
            "option_c": "Reverse rows then transpose",
            "option_d": "Create new matrix",
            "correct_answer": "A",
            "explanation": "Transpose matrix (swap matrix[i][j] with matrix[j][i]), then reverse each row.",
            "xp_reward": 15
        },
        {
            "title": "Spiral Matrix Traversal",
            "description": "Print elements of matrix in spiral order. What's the time complexity?",
            "difficulty": "Medium",
            "topic": "Matrix",
            "option_a": "O(n)",
            "option_b": "O(n²)",
            "option_c": "O(n log n)",
            "option_d": "O(2^n)",
            "correct_answer": "B",
            "explanation": "Must visit each of n² elements exactly once, giving O(n²) time complexity.",
            "xp_reward": 15
        },
        
        # Verbal Aptitude - Synonyms (Hard)
        {
            "title": "Synonym: Obfuscate",
            "description": "Choose the word that is closest in meaning to 'obfuscate':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Clarify",
            "option_b": "Confuse",
            "option_c": "Illuminate",
            "option_d": "Simplify",
            "correct_answer": "B",
            "explanation": "'Obfuscate' means to make something unclear or confusing, often intentionally. The correct synonym is 'confuse'.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Sagacious",
            "description": "Select the synonym for 'sagacious':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Foolish",
            "option_b": "Wise",
            "option_c": "Hasty",
            "option_d": "Weak",
            "correct_answer": "B",
            "explanation": "'Sagacious' means having keen judgment or wisdom. It describes someone who is perceptive and wise.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Inimical",
            "description": "Which of the following is most similar in meaning to 'inimical'?",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Friendly",
            "option_b": "Hostile",
            "option_c": "Favorable",
            "option_d": "Neutral",
            "correct_answer": "B",
            "explanation": "'Inimical' means harmful, unfriendly, or hostile. It describes something that is damaging or antagonistic.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Pulchritude",
            "description": "Pick the word that best matches the meaning of 'pulchritude':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Beauty",
            "option_b": "Strength",
            "option_c": "Cruelty",
            "option_d": "Wisdom",
            "correct_answer": "A",
            "explanation": "'Pulchritude' is a formal or literary word meaning physical beauty or attractiveness.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Perfunctory",
            "description": "Choose the synonym for 'perfunctory':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Thorough",
            "option_b": "Superficial",
            "option_c": "Enthusiastic",
            "option_d": "Deliberate",
            "correct_answer": "B",
            "explanation": "'Perfunctory' describes something done with minimal effort, care, or interest - merely as a routine duty. It is superficial or cursory.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Recalcitrant",
            "description": "Identify the word closest in meaning to 'recalcitrant':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Obedient",
            "option_b": "Stubborn",
            "option_c": "Passive",
            "option_d": "Flexible",
            "correct_answer": "B",
            "explanation": "'Recalcitrant' means resistant to authority, difficult to manage, or stubbornly uncooperative.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Lachrymose",
            "description": "Select the synonym for 'lachrymose':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Tearful",
            "option_b": "Joyful",
            "option_c": "Angry",
            "option_d": "Calm",
            "correct_answer": "A",
            "explanation": "'Lachrymose' means given to tears or weeping; tearful or very sad. It can also describe something that induces tears.",
            "xp_reward": 20
        }
    ]
    
    for question_data in questions_data:
        # Check if question already exists
        existing = db.query(models.Question).filter(models.Question.title == question_data["title"]).first()
        if not existing:
            question = models.Question(**question_data)
            db.add(question)
            print(f"✅ Created question: {question_data['title']}")
        else:
            print(f"⏭️  Question already exists: {question_data['title']}")
    
    db.commit()
    print(f"\n✅ Question seeding complete! Total: {len(questions_data)} questions")


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...\n")
    
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed badges
        print("📛 Seeding badges...")
        seed_badges(db)
        
        print("\n" + "="*80 + "\n")
        
        # Seed questions
        print("❓ Seeding questions...")
        seed_questions(db)
        
        print("\n" + "="*80)
        print("🎉 Database seeding completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
