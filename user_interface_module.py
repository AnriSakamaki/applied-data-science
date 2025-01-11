import argparse
import shlex

import database_module as dm

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''General command line structure: [first_name] [last_name] [argument] [--limit n] -
                    Note that in order to use --actor you have to provide "None" for first and last name.'''
    )

    parser.add_argument('first_name', type=str, help="Actors's first name.")
    parser.add_argument('last_name', type=str, help="Actors's last name.")
    parser.add_argument('--actors', action='store_true', help='Retrieve all actor names. ~ None None --actors')
    parser.add_argument('--bio', action='store_true', help='Retrieve biography information for a given actor. ~ [first_name] [last_name] --bio')
    parser.add_argument('--movies', action='store_true', help='Retrieve all movies for a given actor. ~ [first_name] [last_name] --movies')
    parser.add_argument('--awards', action='store_true', help='Retrieve all awards for a given actor. ~ [first_name] [last_name] --awards')
    parser.add_argument('--genres', action='store_true', help='Retrieve the genre for a given actor. ~ [first_name] [last_name] --genres')
    parser.add_argument('--ratings', action='store_true', help='Retrieve avg and overall movie rating for a given actor. ~ [first_name] [last_name] --ratings')
    parser.add_argument('--topfive', action='store_true', help='Retrieve top 5 movies for a given actor. ~ [first_name] [last_name] --topfive')
    parser.add_argument('--limit', type=int, default=None, help='Limit the number of items to retrieve. ~ [first_name] [last_name] [argument] --limit n')

    return parser

def process_actors(args):
    print('\nAll available actors:')
    result = dm.get_all_actors()
    for index, (_, name) in enumerate(result):
        print(f'\t{index + 1}. {name}')

def get_actor_id(args):
    result = dm.get_all_actors()
    actor_ids = [actor_id for actor_id, actor_name in result if actor_name == f'{args.first_name} {args.last_name}']
    if len(actor_ids) < 1:
        print(f'\t{args.first_name} {args.last_name} is not a valid actor or actress.')
        return None
    actor_id = actor_ids[0]
    return actor_id

def process_bio(args):
    print(f'\nBiography of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return

    result = dm.get_actor_bio(actor_id)
    print(result[0])

def process_movies(args):
    print(f'\nMovies of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return

    result = dm.get_actor_movies(actor_id)
    for index, (_, _, movie_name, _, movie_year, _, _) in enumerate(result):
        if args.limit is not None and index >= args.limit:
            break
        print(f'\t{index + 1}. {movie_name} ({movie_year})')

def process_awards(args):
    print(f'\nAwards of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return

    result = dm.get_actor_awards(actor_id)
    for index, (_, _, award_name, _, award_year) in enumerate(result):
        if args.limit is not None and index >= args.limit:
            break
        print(f'\t{index + 1}. {award_name} ({award_year})')

def process_genres(args):
    print(f'\nGenres of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return

    result = dm.get_actor_genres(actor_id)
    movie_genres = []
    for index, (movie_genre, ) in enumerate(result):
        movie_genres += movie_genre.split(', ')
    movie_genres = list(set(movie_genres))

    for index, movie_genre in enumerate(movie_genres):
        if args.limit is not None and index >= args.limit:
            break
        print(f'\t{index + 1}. {movie_genre}')

def process_ratings(args):
    print(f'\nMovie Ratings (Overall and Yearly) of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return

    result = dm.get_actor_movies_average_rating(actor_id)
    avg_movie_rating = result[0]
    print(f'\tAverage overall movie rating: {round(avg_movie_rating, 2)}')

    result = dm.get_actor_movies(actor_id)
    year_to_rating_map = {}
    for index, (_, _, movie_name, movie_rating, movie_year, _, _) in enumerate(result):
        if movie_year in list(year_to_rating_map.keys()):
            year_to_rating_map[movie_year].append(float(movie_rating))
        else:
            year_to_rating_map[movie_year] = [float(movie_rating)]
    for index, movie_year in enumerate(list(year_to_rating_map.keys())):
        if args.limit is not None and index >= args.limit:
            break
        print(f'\tAverage movie rating in year {movie_year}: {round(sum(year_to_rating_map[movie_year])/len(year_to_rating_map[movie_year]), 2)}')

def process_topfive(args):
    print(f'\nTop 5 movies of {args.first_name} {args.last_name}:')
    actor_id = get_actor_id(args)
    if actor_id is None:
        return
    
    result = dm.get_actor_top_five_movies(actor_id)
    for index, (_, movie_name, movie_rating, movie_year, movie_genre, _, _) in enumerate(result):
        if args.limit is not None and index >= args.limit:
            break
        print(f'\t{movie_rating}: {movie_name} ({movie_year}) - {movie_genre}')
    
if __name__ == '__main__':
    parser = parse_arguments()
    while True:
        input_string = input('Please provide a actors name or use --help to get information about possible functions (Write Q to quit):\n\t')
        if input_string == 'Q':
            break
        args = parser.parse_args(shlex.split(input_string))
        if args.actors:
            process_actors(args)
        if args.bio:
            process_bio(args)
        if args.movies:
            process_movies(args)
        if args.awards:
            process_awards(args)
        if args.genres:
            process_genres(args)
        if args.ratings:
            process_ratings(args)
        if args.topfive:
            process_topfive(args)

    dm.conn.commit()
    dm.conn.close()