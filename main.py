def parseData(filename):
    """ Takes file data and parses neighborhoods and home buyers data to return a dict of neighborhoods and a dict of home buyer """

    with open(filename, "r") as file:
        lines = file.readlines()
	
    neighborhoods = {}
    home_buyers = {}
    for line in lines:
        if line.startswith("N"):
            parts = line.strip().split()
            neighborhood = parts[1]
            scores = {key: int(value) for key, value in (score.split(":") for score in parts[2:])}
            neighborhoods[neighborhood] = scores
        elif line.startswith("H"):
            parts = line.strip().split()
            buyer = parts[1] # H0
            goals = {key: int(value) for key, value in (goal.split(":") for goal in parts[2:5])}
            preferences = parts[5].split(">")
            assigned = "None"
            home_buyers[buyer] = {"goals": goals, "preferences": preferences, "assigned": assigned}
	
    return neighborhoods, home_buyers

def fitscore(home_buyers, neighborhoods):
    """ Calculates home buyer fit scores (home buyer goals * neighborhood attributes) """

    fit_scores = {}
    
    for buyer, data in home_buyers.items():
        fit_scores[buyer] = {neighborhood: sum(data["goals"][key] * neighborhoods[neighborhood][key] for key in data["goals"]) for neighborhood in neighborhoods}
        fit_scores[buyer]['pref'] = data['preferences']
        fit_scores[buyer]['assigned'] = data['assigned']

    return fit_scores

def sortBuyers(fit_scores, neighborhoods, balance):
    """ Sorts home buyers by fit scores in descending order and distributes home buyers into neighborhoods evenly """

    sorted_buyers = []

    # Assigns home buyers to initial neighborhood until full based on balanced data
    for neighborhood in neighborhoods:
        sorted_buyers = sorted(fit_scores.items(), key=lambda x: x[1][neighborhood], reverse=True)
        neighborhoods[neighborhood]['count'] = 0

        for buyer in sorted_buyers:
            if neighborhoods[neighborhood]['count'] < balance:
                if buyer[1]['pref'][0] == neighborhood and buyer[1]['assigned'] == "None":
                    buyer[1]['assigned'] = neighborhood
                    neighborhoods[neighborhood]['count'] += 1

    # Assigns home buyers who were not assigned a neighborhood; neighborhood was full - recursive check
    for buyer in sorted_buyers:
        if buyer[1]['assigned'] == "None":
            pref = buyer[1]['pref']
            sorted_buyer = next((buyer for buyer in reversed(sorted_buyers) if buyer[1]['assigned'] == pref[1]), None)

            # Could improve on this later
            if neighborhoods[buyer[1]['pref'][1]]['count'] < balance:
                buyer[1]['assigned'] = buyer[1]['pref'][1]
            elif neighborhoods[buyer[1]['pref'][1]]['count'] >= balance and sorted_buyer[1][pref[1]] < buyer[1][pref[1]]:
                buyer[1]['assigned'] = buyer[1]['pref'][1]
                sorted_buyer[1]['assigned'] = "None"
            elif neighborhoods[buyer[1]['pref'][2]]['count'] < balance:
                buyer[1]['assigned'] = buyer[1]['pref'][2]
            elif neighborhoods[buyer[1]['pref'][2]]['count'] >= balance and sorted_buyer[1][pref[2]] < buyer[1][pref[2]]:
                buyer[1]['assigned'] = buyer[1]['pref'][2]
                sorted_buyer[1]['assigned'] = "None"        

def make_file(output_file, neighborhoods, fit_scores):
    """ Writes data to output file """

    with open(output_file, 'w') as file:
        for neighborhood, data in neighborhoods.items():
            assigned_buyers = [buyer for buyer, details in fit_scores.items() if details['assigned'] == neighborhood]
            sorted_buyers = sorted(assigned_buyers, key=lambda x: fit_scores[x][neighborhood], reverse=True)
            assigned_buyers_info = " ".join(f"{buyer}({fit_scores[buyer][neighborhood]})" for buyer in sorted_buyers)
            file.write(f"{neighborhood}: {assigned_buyers_info}\n")

def main(input, output):
    neighborhoods, home_buyers = parseData(input)
    fit_scores = fitscore(home_buyers, neighborhoods)
    balance = int(len(home_buyers) / len(neighborhoods))
    sortBuyers(fit_scores, neighborhoods, balance)
    make_file(output, neighborhoods, fit_scores)

if __name__ == "__main__":
    input_file = "./input.txt"
    output_file = "./output.txt"
    main(input_file, output_file)