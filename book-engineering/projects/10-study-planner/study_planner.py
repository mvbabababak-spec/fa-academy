"""Three-day learning log, using only Python's standard library."""

def main():
    total = 0
    for day in range(1, 4):
        while True:
            try:
                raw = input(f'Day {day} minutes (0-1440): ')
                minutes = int(raw)
                if not 0 <= minutes <= 1440:
                    print('Enter a whole number from 0 to 1440.')
                    continue
                break
            except ValueError:
                print('Enter a whole number from 0 to 1440.')
            except EOFError:
                print('\nInput ended; no result calculated.')
                return
        total += minutes
    print(f'Total: {total} minutes')
    print(f'Average: {total / 3:.1f} minutes')
    if total >= 180:
        print('Goal reached')
    else:
        print('Keep practicing')


if __name__ == '__main__':
    main()
