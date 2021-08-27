import click
from click import IntRange

def Not(form):
    return "!" + form

def BigAnd(forms):
    if not forms:
        return "true"
    else:
        return "(" + " && ".join(forms) + ")"

def And(form1, form2):
    return BigAnd([form1, form2])

def And3(form1, form2, form3):
    return BigAnd([form1, form2, form3])

def BigOr(forms):
    if not forms:
        return "false"
    else:
        return "(" + " || ".join(forms) + ")"

def IfThen(form1, form2):
    return "(" + form1 + " -> " + form2 + ")"

def Iff(form1, form2):
    return "(" + form1 + " <-> " + form2 + ")"

def Next(form):
    return "X[!] " + form

def WeakNext(form):
    return "X " + form

def Globally(form):
    return "G " + form

def Eventually(form):
    return "F " + form

def Until(form1, form2):
    return "(" + form1 + " U " + form2 + ")"

def init_counter(i):
    return "init_counter_" + str(i)

def inc(player):
    return "inc_" + player

def counter(player, i):
    return "counter_" + player + "_" + str(i)

def carry(player, i):
    return "carry_" + player + "_" + str(i)

@click.command("gen_counters")
@click.option(
    "--number", type=IntRange(min=0), default=20, help="Number of bits."
)
def main(number):
    for n in range(1,number+1):
        env = "env"
        sys = "sys"

        inputs = [init_counter(i) for i in range(n)] + \
                 [inc(env)]

        outputs = [counter(player, i) for i in range(n) for player in [env, sys]] + \
                  [carry(player, i) for i in range(n) for player in [env, sys]] + \
                  [inc(sys)]

        preset = [And(IfThen(Next(counter(env, i)), init_counter(i)),
                      IfThen(init_counter(i), WeakNext(counter(env, i)))) for i in range(n)] + \
                 [Not(counter(sys, i)) for i in range(n)] + \
                 [Not(inc(sys))]

        require = [IfThen(inc(env), Not(Next(inc(env))))]

        asserts = [IfThen(Next(carry(env, 0)), inc(env))] + \
                  [IfThen(inc(env), WeakNext(carry(env, 0)))] + \
                  [Iff(carry(sys, 0), inc(sys))] + \
                  [IfThen(Next(carry(player, i)), And(counter(player, i - 1),
                                               Next(carry(player, i - 1))))
                   for i in range(1, n)
                   for player in [env, sys]] + \
                  [IfThen(And(counter(player, i - 1),
                              WeakNext(carry(player, i - 1))),
                          WeakNext(carry(player, i)))
                   for i in range(1, n)
                   for player in [env, sys]] + \
                  [And(IfThen(Next(counter(player, i)),
                              Not(Iff(counter(player, i), Next(carry(player, i))))),
                       IfThen(Not(Iff(counter(player, i), WeakNext(carry(player, i)))),
                              WeakNext(counter(player, i))))
                   for i in range(n)
                   for player in [env, sys]]

        guarantee = Next(Eventually(BigAnd([Iff(counter(env, i), counter(sys, i))
                                            for i in range(n)])))

        env_assumption = Globally(BigAnd(require))

        monolithic = And(BigAnd(preset),
                         IfThen(env_assumption,
                                And(Next(Globally(BigAnd(asserts))), guarantee)))

        # factors = preset + \
        #           map(lambda form : Next(Globally(form)), asserts) + \
        #           [IfThen(env_assumption, guarantee)]

        save_path = "../../../Two-player-Game/Double-Counter/System-first/"

        mf = open(save_path+"counters_" + str(n) + ".ltlf", "w")
        mf.write(monolithic)

        # ff = open("counters_" + str(n) + ".fact", "w")
        # for factor in factors:
        #     ff.write(factor + "\n")

        pf = open(save_path+"counters_" + str(n) + ".part", "w")
        pf.write(".inputs: " + " ".join(map(lambda var : var.lower(), inputs)) + "\n")
        pf.write(".outputs: " + " ".join(map(lambda var : var.lower(), outputs)))


if __name__ == '__main__':
    main()