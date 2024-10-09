import Booker
import argparse

# Example usage:
# python main.py --days 1 3 --start-hour 10 --end-hour 18 --max-bookings-per-day 5 --confirm --headless

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Run the Booker class with specified options.')

    # Add arguments
    parser.add_argument('--days', nargs='+', type=int, default=[1, 3], help='List of days for booking (e.g., 1 2 3)')
    parser.add_argument('--start-hour', type=int, default=12, help='Start hour for bookings')
    parser.add_argument('--end-hour', type=int, default=16, help='End hour for bookings')
    parser.add_argument('--max-bookings-per-day', type=int, default=3, help='Maximum bookings per day')
    parser.add_argument('--confirm', action='store_true', default=False, help='Require confirmation for bookings')
    parser.add_argument('--headless', action='store_true', default=False, help='Run in headless mode')

    # Parse arguments
    args = parser.parse_args()

    # Create Booker instance
    booker = Booker.Booker(
        days=args.days,
        start_hour=args.start_hour,
        end_hour=args.end_hour,
        max_bookings_per_day=args.max_bookings_per_day,
        confirm=args.confirm,
        headless=args.headless
    )

    # Run the Booker instance
    booker.run()

if __name__ == '__main__':
    main()
