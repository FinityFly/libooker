import Booker

booker = Booker.Booker(days=[1, 2, 3], start_hour=11, end_hour=16, headless=True)
booker.run()