from combat.actors import Actor

if __name__ == "__main__":

    levels = range(1, 13)

    for count in levels:
        print(f"\count: {count}")
        modifier = 1
        encounter_scaling = 1
        attack_count = 1
        if count > 1:
            encounter_scaling = count * 0.7
            print(encounter_scaling)
            attack_count = max(1, int(encounter_scaling))
            print(attack_count)
            encounter_scaling = (
                count / attack_count * Actor.OPPONENT_ENCOUNTER_SCALING_FACTOR
            )
            print(encounter_scaling)
            print(attack_count * encounter_scaling)
