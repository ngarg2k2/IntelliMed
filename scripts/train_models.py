from app.db import Base, SessionLocal, engine
from app.ml import train_demand_model, train_symptom_model
from app.seed import seed_database


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_database(db)
        train_symptom_model()
        train_demand_model(db)
    print("Trained symptom classifier and inventory demand forecaster.")


if __name__ == "__main__":
    main()
