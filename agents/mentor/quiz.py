#!/usr/bin/env python3
"""
MindBridge Mentor - Daily Quiz System
10 cards per session: 5 review + 5 new
Includes concept, simulation, and interview modes
"""
import sqlite3
import os
import sys
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "mentor.db")

TYPE_LABELS = {
    "simulation": "🎭 SIMULATION",
    "interview":  "🎤 INTERVIEW",
    "concept":    "💡 CONCEPT",
}


def get_conn():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found. Run: python agents/mentor/init_db.py")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def detect_card_type(question):
    q = question.upper()
    if "SIMULATION" in q:
        return "simulation"
    if "INTERVIEW" in q:
        return "interview"
    return "concept"


def get_review_cards(limit=5):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("""
        SELECT id, topic, question, ideal_answer, times_reviewed, times_correct
        FROM flashcards
        WHERE next_review <= ? AND times_reviewed > 0
        ORDER BY next_review ASC LIMIT ?
    """, (today, limit))
    cards = [
        {"id": r[0], "topic": r[1], "question": r[2],
         "ideal_answer": r[3], "times_reviewed": r[4],
         "times_correct": r[5], "is_new": False}
        for r in c.fetchall()
    ]
    conn.close()
    return cards


def get_new_cards(limit=5):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, topic, question, ideal_answer, times_reviewed, times_correct
        FROM flashcards
        WHERE times_reviewed = 0
        ORDER BY week ASC, id ASC LIMIT ?
    """, (limit,))
    cards = [
        {"id": r[0], "topic": r[1], "question": r[2],
         "ideal_answer": r[3], "times_reviewed": r[4],
         "times_correct": r[5], "is_new": True}
        for r in c.fetchall()
    ]
    conn.close()
    return cards


def update_card_schedule(card_id, quality):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT ease_factor, interval_days, repetitions FROM flashcards WHERE id=?",
        (card_id,),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return None

    ef, interval, reps = row

    if quality < 3:
        reps = 0
        interval = 1
    else:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        elif reps == 2:
            interval = 7
        else:
            interval = round(interval * ef)
        reps += 1
        ef = max(1.3, ef + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    next_review = (date.today() + timedelta(days=interval)).isoformat()
    correct = 1 if quality >= 3 else 0

    c.execute("""
        UPDATE flashcards
        SET ease_factor=?, interval_days=?, repetitions=?,
            next_review=?, times_reviewed=times_reviewed+1,
            times_correct=times_correct+?
        WHERE id=?
    """, (ef, interval, reps, next_review, correct, card_id))

    conn.commit()
    conn.close()
    return {"next_review": next_review, "interval_days": interval}


def run_quiz():
    print("\n" + "═" * 70)
    print("   🏥 MINDBRIDGE MENTOR — Daily Quiz")
    print("   🎯 Target: Healthcare AI Engineer ($200K-$300K)")
    print("═" * 70)

    review_cards = get_review_cards(limit=5)
    new_cards = get_new_cards(limit=5)

    # Fill gaps
    if len(review_cards) < 5:
        new_cards = get_new_cards(limit=10 - len(review_cards))
    if len(new_cards) < 5 and len(review_cards) > 0:
        review_cards = get_review_cards(limit=10 - len(new_cards))

    all_cards = review_cards + new_cards

    if not all_cards:
        print("\n🎉 All caught up! No cards due today. Come back tomorrow.\n")
        return

    total = len(all_cards)
    print(f"\n  📊 Today's Session:")
    print(f"     🔄 Review:  {len(review_cards)} cards  (spaced repetition)")
    print(f"     ✨ New:     {len(new_cards)} cards  (fresh learning)")
    print(f"     📝 Total:   {total} questions\n")
    input("  Press ENTER to begin ▶\n")

    score = 0
    results = []

    for i, card in enumerate(all_cards, 1):
        card_type = detect_card_type(card["question"])
        type_label = TYPE_LABELS.get(card_type, "💡 CONCEPT")
        badge = "✨ NEW" if card["is_new"] else "🔄 REVIEW"

        print("─" * 70)
        print(f"  [{i}/{total}]  {badge}  |  {type_label}  |  {card['topic']}")
        if not card["is_new"] and card["times_reviewed"] > 0:
            acc = round(card["times_correct"] / card["times_reviewed"] * 100)
            print(f"  History: reviewed {card['times_reviewed']}x, {acc}% accuracy")
        print("─" * 70)

        # Question display
        q = card["question"]
        for prefix in ["SIMULATION: ", "INTERVIEW SIMULATION: ", "INTERVIEW: "]:
            q = q.replace(prefix, "")

        if card_type == "simulation":
            print("\n  🎭 Respond as if this is a real scenario:\n")
        elif card_type == "interview":
            print("\n  🎤 Answer as if speaking to a hiring manager:\n")
        else:
            print()

        print(f"  ❓ {q}\n")
        input("  💭 Think... Press ENTER to reveal answer ▶")

        print("\n" + "─" * 70)
        print("  ✅ IDEAL ANSWER:")
        print("─" * 70 + "\n")
        print(f"  {card['ideal_answer']}\n")

        print("  How well did you know this?")
        print("  1=❌ No idea  2=😓 Partial  3=✓ Good  4=⭐ Perfect")

        while True:
            rating = input("\n  Rating (1-4): ").strip()
            if rating in ["1", "2", "3", "4"]:
                break

        rating = int(rating)
        result = update_card_schedule(card["id"], rating)
        correct = rating >= 3

        if correct:
            score += 1
            days = result["interval_days"] if result else 1
            print(f"\n  ✓ Correct! Next review in {days} day(s)")
        else:
            print(f"\n  ✗ Missed — comes back tomorrow!")

        results.append({
            "q": q[:50],
            "type": card_type,
            "rating": rating,
            "new": card["is_new"]
        })
        print()

    # Summary
    pct = round(score / total * 100)
    print("═" * 70)
    print(f"  📊 SESSION COMPLETE! Score: {score}/{total} ({pct}%)")
    print("═" * 70)

    if pct == 100:
        print("  🏆 PERFECT! You nailed every question!")
    elif pct >= 80:
        print("  ⭐ Strong session! Keep this up!")
    elif pct >= 60:
        print("  👍 Good progress! Review the ones you missed.")
    else:
        print("  💪 Keep going — every session builds toward that $200K+ role!")

    icons = {1: "❌", 2: "😓", 3: "✓ ", 4: "⭐"}
    t_short = {"simulation": "SIM", "interview": "INT", "concept": "CON"}
    print("\n  Breakdown:")
    for r in results:
        badge = "NEW" if r["new"] else "REV"
        print(f"    {icons[r['rating']]} [{badge}][{t_short[r['type']]}] {r['q']}...")

    print(f"\n  🎯 Every answer mastered = closer to $200K-$300K")
    print(f"  ⏰ See you tomorrow at 8 AM!\n")
    print("═" * 70 + "\n")


def show_progress():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM flashcards")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM flashcards WHERE times_reviewed > 0")
    reviewed = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM flashcards WHERE times_reviewed = 0")
    unseen = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM flashcards WHERE next_review <= date('now')")
    due = c.fetchone()[0]
    c.execute("SELECT SUM(times_correct), SUM(times_reviewed) FROM flashcards WHERE times_reviewed > 0")
    row = c.fetchone()
    acc = round(row[0] / row[1] * 100) if row[0] and row[1] else 0
    c.execute("SELECT COUNT(*) FROM flashcards WHERE question LIKE '%SIMULATION%'")
    sims = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM flashcards WHERE question LIKE '%INTERVIEW%'")
    ints = c.fetchone()[0]
    c.execute("SELECT week, topic, phase, status FROM curriculum_progress ORDER BY week")
    curriculum = c.fetchall()
    conn.close()

    print("\n" + "═" * 70)
    print("  📊 MINDBRIDGE MENTOR — Progress Dashboard")
    print("═" * 70)
    print(f"\n  🃏 Cards:      {total} total  |  {reviewed} reviewed  |  {unseen} new  |  {due} due today")
    print(f"  🎯 Accuracy:  {acc}%")
    print(f"  📚 Types:     💡 {total-sims-ints} concept  |  🎭 {sims} simulation  |  🎤 {ints} interview")

    print(f"\n  🗓️  12-Week Curriculum:\n")
    phase_labels = {
        "foundation": "MONTH 1: FOUNDATION",
        "expertise":  "MONTH 2: EXPERTISE",
        "interview":  "MONTH 3: INTERVIEW PREP",
    }
    cur_phase = None
    for week, topic, phase, status in curriculum:
        if phase != cur_phase:
            if cur_phase:
                print()
            cur_phase = phase
            print(f"  [{phase_labels.get(phase, phase.upper())}]")
        icon = {"available": "🟢", "in_progress": "🔵",
                "completed": "✅", "locked": "🔒"}.get(status, "◯")
        print(f"    {icon} Week {week:2d}: {topic}")

    print(f"\n  💡 Run quiz: python agents/mentor/quiz.py")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "progress":
        show_progress()
    else:
        run_quiz()
