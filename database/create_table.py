import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import Base, engine
from database.models import Post, Product, Staff, Order, Client, ListOrderedGoods


def main():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)



if __name__ == "__main__":
   main()
