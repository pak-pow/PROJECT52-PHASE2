from app import create_app
from app.models import board_model, column_model, card_model

app = create_app()

def seed_data():
    with app.app_context():
        existing_boards = board_model.get_all_boards()
        if len(existing_boards) > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        b1_id = board_model.create_board("Work Projects", "Phase 2 Sprint Tasks", "#6366f1")
        b1_c1 = column_model.create_column(b1_id, "Backlog")
        b1_c2 = column_model.create_column(b1_id, "In Progress")
        b1_c3 = column_model.create_column(b1_id, "Done")

        card_model.create_card(b1_c1, "Research competitors", "Look at Trello and Linear UI/UX")
        card_model.create_card(b1_c1, "Write PRD", "Product requirements document")
        card_model.create_card(b1_c2, "Build API routes", "Board, Column, and Card endpoints")
        card_model.create_card(b1_c3, "Database schema", "SQLite with cascade deletes")

        b2_id = board_model.create_board("Personal", "Life admin and habits", "#10b981")
        b2_c1 = column_model.create_column(b2_id, "To Do")
        b2_c2 = column_model.create_column(b2_id, "Doing")
        b2_c3 = column_model.create_column(b2_id, "Done")

        card_model.create_card(b2_c1, "Buy groceries", "Milk, eggs, coffee")
        card_model.create_card(b2_c1, "Read book", "System Design Interview prep")
        card_model.create_card(b2_c2, "Learn Kanban architecture", "Understand positional tracking")
        card_model.create_card(b2_c3, "Morning run", "Completed 5km")

        print("Seeding complete! Added 2 boards, 6 columns, and 8 cards.")

if __name__ == "__main__":
    seed_data()