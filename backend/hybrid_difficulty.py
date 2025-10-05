"""
Hybrid Difficulty Rating System
Combines heuristic-based initial difficulty with user performance data
"""
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import datetime
import re


class DifficultyCalculator:
    """
    Hybrid approach for question difficulty rating
    
    Phase 1: Heuristic-based initial assignment
    Phase 2: Refine with user performance data
    Phase 3: Dynamic adjustment with weighted average
    """
    
    def __init__(self):
        self.difficulty_map = {
            "Easy": 0.3,
            "Medium": 0.6,
            "Hard": 0.9
        }
        self.reverse_map = {
            (0, 0.4): "Easy",
            (0.4, 0.7): "Medium",
            (0.7, 1.0): "Hard"
        }
    
    def calculate_heuristic_score(self, question: dict) -> float:
        """
        Calculate initial difficulty score (0-1) based on heuristics
        
        Factors:
        1. Topic complexity (30%)
        2. Description length & complexity (20%)
        3. Explanation length (10%)
        4. Option similarity (20%) - harder if options are similar
        5. Current manual difficulty (20%)
        """
        score = 0.0
        
        # 1. Topic complexity (30% weight)
        topic_difficulty = self._get_topic_difficulty(question.get('topic', ''))
        score += topic_difficulty * 0.3
        
        # 2. Description complexity (20% weight)
        desc_score = self._analyze_description(question.get('description', ''))
        score += desc_score * 0.2
        
        # 3. Explanation length (10% weight) - longer explanation = harder
        explanation = question.get('explanation', '')
        exp_score = min(len(explanation) / 500, 1.0)  # Normalize to 0-1
        score += exp_score * 0.1
        
        # 4. Option similarity (20% weight) - similar options = harder
        options = [
            question.get('option_a', ''),
            question.get('option_b', ''),
            question.get('option_c', ''),
            question.get('option_d', '')
        ]
        similarity_score = self._calculate_option_similarity(options)
        score += similarity_score * 0.2
        
        # 5. Current manual difficulty (20% weight)
        manual_diff = question.get('difficulty', 'Medium')
        score += self.difficulty_map.get(manual_diff, 0.6) * 0.2
        
        return min(max(score, 0.0), 1.0)  # Clamp to [0, 1]
    
    def _get_topic_difficulty(self, topic: str) -> float:
        """
        Assign difficulty based on topic complexity
        
        Easy: Basic arithmetic, simple concepts
        Medium: Multi-step problems, moderate reasoning
        Hard: Advanced concepts, complex reasoning
        """
        easy_topics = [
            'Simple Interest', 'Averages', 'Percentages', 'Ratio and Proportion',
            'Ages', 'Calendar', 'Clocks', 'Number Series'
        ]
        
        hard_topics = [
            'Profit and Loss', 'Compound Interest', 'Time and Work',
            'Speed and Distance', 'Probability', 'Permutations', 'Combinations',
            'Data Interpretation', 'Synonyms', 'Antonyms', 'Sentence Completion'
        ]
        
        if topic in easy_topics:
            return 0.25
        elif topic in hard_topics:
            return 0.75
        else:
            return 0.5  # Medium by default
    
    def _analyze_description(self, description: str) -> float:
        """
        Analyze description complexity
        
        Factors:
        - Length (longer = harder)
        - Number of steps/clauses
        - Presence of complex terms
        """
        length_score = min(len(description) / 300, 1.0)
        
        # Count steps (sentences, commas indicate multiple clauses)
        sentences = len(re.split(r'[.!?]', description))
        step_score = min(sentences / 5, 1.0)
        
        # Complex terms (numbers, percentages, fractions)
        complex_terms = len(re.findall(r'\d+%|\d+/\d+|\d+\.\d+', description))
        term_score = min(complex_terms / 5, 1.0)
        
        return (length_score + step_score + term_score) / 3
    
    def _calculate_option_similarity(self, options: list) -> float:
        """
        Calculate how similar the options are
        More similar options = harder question (better distractors)
        """
        if not options or len(options) < 2:
            return 0.5
        
        # Simple approach: check if options are in same range/format
        numeric_options = []
        for opt in options:
            # Extract numbers from options
            numbers = re.findall(r'\d+\.?\d*', opt)
            if numbers:
                try:
                    numeric_options.append(float(numbers[0]))
                except:
                    pass
        
        if len(numeric_options) >= 3:
            # Check if numbers are close (within 20% of each other)
            max_val = max(numeric_options)
            min_val = min(numeric_options)
            if max_val > 0:
                similarity = 1 - ((max_val - min_val) / max_val)
                return min(similarity, 1.0)
        
        # For verbal questions, check length similarity
        lengths = [len(opt) for opt in options]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # Low variance = similar lengths = harder
        similarity = 1 - min(variance / 100, 1.0)
        return similarity
    
    def calculate_performance_difficulty(self, question_id: int, db: Session) -> float:
        """
        Calculate difficulty based on user performance
        
        Factors:
        1. Success rate (60% weight)
        2. Average time taken (30% weight)
        3. User level who got it right (10% weight)
        """
        attempts = db.query(models.QuestionAttempt).filter(
            models.QuestionAttempt.question_id == question_id
        ).all()
        
        if len(attempts) < 5:  # Need minimum data
            return None
        
        # 1. Success rate (inverse: low success = high difficulty)
        correct_count = sum(1 for a in attempts if a.is_correct)
        success_rate = correct_count / len(attempts)
        success_score = 1 - success_rate  # Invert: low success = high difficulty
        
        # 2. Average time taken (normalized)
        total_time = sum(a.time_taken or 0 for a in attempts if a.time_taken)
        avg_time = total_time / len(attempts) if attempts else 0
        # Assume 30s = easy, 60s = medium, 120s = hard
        time_score = min(avg_time / 120, 1.0)
        
        # 3. User level analysis (who's getting it right?)
        correct_attempts = [a for a in attempts if a.is_correct]
        if correct_attempts:
            user_ids = [a.user_id for a in correct_attempts]
            users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
            avg_level = sum(u.level for u in users) / len(users) if users else 5
            # If high-level users are solving it, it might be easier
            level_score = max(0, 1 - (avg_level / 20))  # Normalize to 0-1
        else:
            level_score = 1.0  # Nobody solved it = very hard
        
        # Weighted average
        performance_score = (
            success_score * 0.6 +
            time_score * 0.3 +
            level_score * 0.1
        )
        
        return min(max(performance_score, 0.0), 1.0)
    
    def calculate_hybrid_difficulty(self, heuristic_score: float, 
                                   performance_score: float, 
                                   alpha: float) -> float:
        """
        Combine heuristic and performance scores
        
        new_difficulty = α * heuristic_score + (1-α) * performance_score
        
        α starts high (0.7) and decreases as we gather more data
        """
        if performance_score is None:
            return heuristic_score
        
        hybrid_score = alpha * heuristic_score + (1 - alpha) * performance_score
        return min(max(hybrid_score, 0.0), 1.0)
    
    def score_to_difficulty(self, score: float) -> str:
        """Convert 0-1 score to Easy/Medium/Hard"""
        for (min_val, max_val), difficulty in self.reverse_map.items():
            if min_val <= score < max_val:
                return difficulty
        return "Hard" if score >= 0.7 else "Easy"
    
    def calculate_xp_reward(self, difficulty: str) -> int:
        """Calculate XP reward based on difficulty"""
        xp_map = {
            "Easy": 10,
            "Medium": 15,
            "Hard": 20
        }
        return xp_map.get(difficulty, 15)
    
    def update_alpha(self, total_attempts: int) -> float:
        """
        Decrease alpha (heuristic weight) as we gather more data
        
        Start: α = 0.7 (70% heuristic, 30% performance)
        After 50 attempts: α = 0.5 (50-50)
        After 100+ attempts: α = 0.3 (30% heuristic, 70% performance)
        """
        if total_attempts < 10:
            return 0.8  # Trust heuristic more with little data
        elif total_attempts < 50:
            return 0.7
        elif total_attempts < 100:
            return 0.5
        else:
            return 0.3  # Trust user data more with lots of data


def initialize_heuristic_scores():
    """
    Run this once to calculate initial heuristic scores for all questions
    """
    db = SessionLocal()
    calculator = DifficultyCalculator()
    
    try:
        questions = db.query(models.Question).all()
        updated = 0
        
        print("🔍 Calculating heuristic scores for all questions...\n")
        
        for question in questions:
            # Prepare question dict for heuristic calculation
            q_dict = {
                'topic': question.topic,
                'description': question.description,
                'explanation': question.explanation,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'difficulty': question.difficulty
            }
            
            # Calculate heuristic score
            heuristic_score = calculator.calculate_heuristic_score(q_dict)
            
            # Store initial values
            question.initial_difficulty = question.difficulty
            question.heuristic_score = heuristic_score
            question.alpha_weight = 0.7  # Start with 70% heuristic
            
            print(f"✅ {question.title}")
            print(f"   Manual: {question.difficulty} → Heuristic Score: {heuristic_score:.2f}")
            
            updated += 1
        
        db.commit()
        print(f"\n✅ Initialized heuristic scores for {updated} questions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def update_question_difficulty(question_id: int):
    """
    Update a single question's difficulty based on hybrid approach
    Called after each attempt or periodically
    """
    db = SessionLocal()
    calculator = DifficultyCalculator()
    
    try:
        question = db.query(models.Question).filter(
            models.Question.id == question_id
        ).first()
        
        if not question:
            return
        
        # Calculate performance-based difficulty
        perf_score = calculator.calculate_performance_difficulty(question_id, db)
        
        if perf_score is not None:
            # Update alpha based on attempts
            question.alpha_weight = calculator.update_alpha(question.total_attempts)
            
            # Calculate hybrid difficulty
            hybrid_score = calculator.calculate_hybrid_difficulty(
                question.heuristic_score,
                perf_score,
                question.alpha_weight
            )
            
            question.performance_difficulty = perf_score
            
            # Update difficulty label
            new_difficulty = calculator.score_to_difficulty(hybrid_score)
            
            if new_difficulty != question.difficulty:
                old_difficulty = question.difficulty
                question.difficulty = new_difficulty
                question.xp_reward = calculator.calculate_xp_reward(new_difficulty)
                question.last_difficulty_update = datetime.now()
                
                print(f"Updated: {question.title}")
                print(f"  {old_difficulty} → {new_difficulty}")
                print(f"  Heuristic: {question.heuristic_score:.2f}, Performance: {perf_score:.2f}")
                print(f"  Alpha: {question.alpha_weight:.2f}, Hybrid: {hybrid_score:.2f}")
            
            db.commit()
            
    except Exception as e:
        print(f"Error updating question {question_id}: {e}")
        db.rollback()
    finally:
        db.close()


def batch_update_all_difficulties():
    """
    Run this periodically (daily/weekly) to update all question difficulties
    """
    db = SessionLocal()
    calculator = DifficultyCalculator()
    
    try:
        questions = db.query(models.Question).filter(
            models.Question.total_attempts >= 5  # Only update questions with enough data
        ).all()
        
        updated = 0
        print(f"🔄 Updating difficulties for {len(questions)} questions with sufficient data...\n")
        
        for question in questions:
            perf_score = calculator.calculate_performance_difficulty(question.id, db)
            
            if perf_score is not None:
                question.alpha_weight = calculator.update_alpha(question.total_attempts)
                
                hybrid_score = calculator.calculate_hybrid_difficulty(
                    question.heuristic_score,
                    perf_score,
                    question.alpha_weight
                )
                
                question.performance_difficulty = perf_score
                new_difficulty = calculator.score_to_difficulty(hybrid_score)
                
                if new_difficulty != question.difficulty:
                    print(f"✏️  {question.title}")
                    print(f"   {question.difficulty} → {new_difficulty} (α={question.alpha_weight:.2f})")
                    
                    question.difficulty = new_difficulty
                    question.xp_reward = calculator.calculate_xp_reward(new_difficulty)
                    question.last_difficulty_update = datetime.now()
                    updated += 1
        
        db.commit()
        print(f"\n✅ Updated {updated} question difficulties")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("HYBRID DIFFICULTY RATING SYSTEM")
    print("="*80 + "\n")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Choose an option:")
        print("1. Initialize heuristic scores (run once)")
        print("2. Batch update all difficulties")
        print("3. Show current statistics")
        choice = input("\nEnter choice (1-3): ")
    
    if choice == "1":
        initialize_heuristic_scores()
    elif choice == "2":
        batch_update_all_difficulties()
    elif choice == "3":
        db = SessionLocal()
        questions = db.query(models.Question).all()
        with_data = [q for q in questions if q.total_attempts >= 5]
        
        print(f"\nTotal questions: {len(questions)}")
        print(f"Questions with sufficient data (5+ attempts): {len(with_data)}")
        print(f"Questions needing more data: {len(questions) - len(with_data)}")
        
        if with_data:
            avg_alpha = sum(q.alpha_weight for q in with_data) / len(with_data)
            print(f"Average alpha weight: {avg_alpha:.2f}")
        
        db.close()
