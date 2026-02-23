#!/usr/bin/env python3
"""MindBridge Mentor - Quiz yourself with spaced repetition"""
import sqlite3
from datetime import date
import random

DB_PATH = "mentor.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def get_due_cards(limit=5):
    """Get flashcards due for review today."""
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute(
        "SELECT id, topic, question, ideal_answer, times_reviewed, times_correct "
        "FROM flashcards WHERE next_review <= ? ORDER BY next_review ASC LIMIT ?",
        (today, limit),
    )
    cards = [
        {
            "id": r[0],
            "topic": r[1],
            "question": r[2],
            "ideal_answer": r[3],
            "times_reviewed": r[4],
            "times_correct": r[5],
        }
        for r in c.fetchall()
    ]
    conn.close()
    return cards


def quiz_session():
    """Run an interactive quiz session."""
    cards = get_due_cards(limit=5)
    
    if not cards:
        print("\n🎉 No cards due today! You're all caught up!")
        print("Come back tomorrow for more review.")
        return
    
    print(f"\n📚 MINDBRIDGE MENTOR - Quiz Session")
    print(f"   {len(cards)} flashcards due for review\n")
    print("=" * 70)
    
    score = 0
    for i, card in enumerate(cards, 1):
        print(f"\n[Question {i}/{len(cards)}]")
        print(f"Topic: {card['topic']}")
        print(f"Stats: Reviewed {card['times_reviewed']} times, Correct {card['times_correct']} times\n")
        print(f"❓ {card['question']}")
        print()
        
        input("Press ENTER to see the answer...")
        
        print(f"\n✅ IDEAL ANSWER:")
        print(f"{card['ideal_answer']}")
        print()
        
        while True:
            rating = input("How well did you know this? (1=Forgot, 2=Hard, 3=Good, 4=Easy): ").strip()
            if rating in ['1', '2', '3', '4']:
                rating = int(rating)
                break
            print("Please enter 1, 2, 3, or 4")
        
        if rating >= 3:
            score += 1
            print("✓ Correct!")
        else:
            print("✗ Review this one!")
        
        # Update the card's spaced repetition schedule
        update_card_schedule(card['id'], rating)
        
        if i < len(cards):
            print("\n" + "=" * 70)
    
    print(f"\n📊 SESSION COMPLETE!")
    print(f"   Score: {score}/{len(cards)} ({score/len(cards)*100:.0f}%)")
    
    if score == len(cards):
        print("   🏆 Perfect score! You're crushing it!")
    elif score >= len(cards) * 0.7:
        print("   ⭐ Great work! Keep it up!")
    else:
        print("   💪 Review these concepts and try again tomorrow!")


def update_card_schedule(card_id, quality):
    """Update card using simplified spaced repetition."""
    from datetime import timedelta
    
    conn = get_conn()
    c = conn.cursor()
    
    # Get current card state
    c.execute(
        "SELECT interval_days, repetitions FROM flashcards WHERE id = ?",
        (card_id,),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return
    
    interval, reps = row
    
    # Simplified SM-2 algorithm
    if quality <= 2:
        # Forgot or struggled - reset
        interval = 1
        reps = 0
    else:
        # Good or easy - increase interval
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = interval * 2
        reps += 1
    
    next_review = (date.today() + timedelta(days=interval)).isoformat()
    correct = 1 if quality >= 3 else 0
    
    c.execute(
        "UPDATE flashcards SET interval_days = ?, repetitions = ?, "
        "next_review = ?, times_reviewed = times_reviewed + 1, "
        "times_correct = times_correct + ? WHERE id = ?",
        (interval, reps, next_review, correct, card_id),
    )
    
    conn.commit()
    conn.close()


def show_progress():
    """Show learning progress."""
    conn = get_conn()
    c = conn.cursor()
    
    # Get curriculum progress
    c.execute(
        "SELECT week, topic, phase, status FROM curriculum_progress ORDER BY week"
    )
    curriculum = c.fetchall()
    
    # Get flashcard stats
    c.execute(
        "SELECT COUNT(*) FROM flashcards WHERE times_reviewed > 0"
    )
    reviewed_count = c.fetchone()[0]
    
    c.execute(
        "SELECT COUNT(*) FROM flashcards"
    )
    total_cards = c.fetchone()[0]
    
    conn.close()
    
    print("\n📊 MINDBRIDGE MENTOR - Learning Progress")
    print("=" * 70)
    print(f"\n📚 Flashcards: {reviewed_count}/{total_cards} reviewed")
    print(f"\n🎯 12-Week Curriculum:\n")
    
    for week, topic, phase, status in curriculum:
        status_icon = "🟢" if status == "available" else "🔒" if status == "locked" else "✅"
        print(f"  {status_icon} Week {week:2d}: {topic} ({phase})")
    
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "progress":
        show_progress()
    else:
        quiz_session()
