import math

if __name__ == "__main__":

    max_hits = 10
    max_participants = 7
    participants = range(1, max_participants + 1)

    for encounter_scale in participants:
        print(f"participants: {encounter_scale}/{max_participants}")

        for hits_init in range(1, 8):
            factor = hits_init / max_hits
            attack_count_scaling = pow(1 - factor, 7)
            scaling = 1 + (encounter_scale * attack_count_scaling)
            hits = hits_init * scaling
            print(
                f"{attack_count_scaling:.2f} | {scaling:.2f} | {hits_init} | {hits:.2f} "
            )
