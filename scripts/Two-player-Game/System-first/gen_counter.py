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

def counter(i):
    return "counter_" + str(i)

def carry(i):
    return "carry_" + str(i)


@click.command("gen_counter")
@click.option(
    "--number", type=IntRange(min=0), default=20, help="Number of bits."
)
def main(number):
    for n in range(1,number+1):
        inc = "inc"

        inputs = [init_counter(i) for i in range(n)] + \
                 [inc]

        outputs = [counter(i) for i in range(n)] + \
                  [carry(i) for i in range(n)]

        preset = [And(IfThen(Next(counter(i)), init_counter(i)),
                      IfThen(init_counter(i), WeakNext(counter(i)))) for i in range(n)]

        require = [IfThen(Not(inc), Next(inc))]

        asserts = [IfThen(Next(carry(0)), inc)] + \
                  [IfThen(inc, WeakNext(carry(0)))] + \
                  [IfThen(Next(carry(i)), And(counter(i - 1),
                                              Next(carry(i - 1))))
                   for i in range(1, n)] + \
                  [IfThen(And(counter(i - 1),
                              WeakNext(carry(i - 1))),
                          WeakNext(carry(i)))
                   for i in range(1, n)] + \
                  [And(IfThen(Next(counter(i)),
                              Not(Iff(counter(i), Next(carry(i))))),
                       IfThen(Not(Iff(counter(i), WeakNext(carry(i)))),
                              WeakNext(counter(i))))
                   for i in range(n)]

        guarantee = Next(Eventually(BigAnd([Not(counter(i)) for i in range(n)])))

        env_assumption = Globally(BigAnd(require))

        monolithic = And(BigAnd(preset),
                         IfThen(env_assumption,
                                And(Next(Globally(BigAnd(asserts))), guarantee)))

        # factors = preset + \
        #           map(lambda form : Globally(form), asserts) + \
        #           [IfThen(env_assumption, guarantee)]

        save_path = "../../../Two-player-Game/Single-Counter/System-first/"
        mf = open(save_path+"counter_" + str(n) + ".ltlf", "w")
        mf.write(monolithic)

        # ff = open("benchmarks/counter/counter_" + str(n) + ".fact", "w")
        # for factor in factors:
        #     ff.write(factor + "\n")

        pf = open(save_path+"counter_" + str(n) + ".part", "w")
        pf.write(".inputs " + " ".join(map(lambda var : var.lower(), inputs)) + "\n")
        pf.write(".outputs " + " ".join(map(lambda var : var.lower(), outputs)))

if __name__ == '__main__':
    main()

# tf = open("tlsf/counter/counter_" + str(n) + ".tlsf", "w")
# lines = [ "INFO {"
# , "  TITLE: \"Counter (n = " + str(n) + ")\""
# , "  DESCRIPTION: \"Counter game\""
# , "  SEMANTICS: Mealy"
# , "  TARGET: Mealy"
# , "}"
# , "MAIN {"
# , "  INPUTS {"
# , ";\n".join(inputs) + ";"
# , "  }"
# , "  OUTPUTS {"
# , ";\n".join(outputs) + ";"
# , "  }"
# , "  PRESET {"
# , ";\n".join(preset) + ";"
# , "  }"
# , "  REQUIRE {"
# , ";\n".join(require) + ";"
# , "  }"
# , "  ASSERT {"
# , ";\n".join(asserts) + ";"
# , "  }"
# , "  GUARANTEE {"
# , guarantee + ";"
# , "  }"
# , "}"
# ]
# for line in lines:
#     tf.write(line + "\n")
