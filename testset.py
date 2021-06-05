testset = [
    {
        "input": ("On earth, the atmosphere protects us from the sun, but not enough so we use sunscreen", 
                  "The nucleus, which is positively charged, and the electrons which are negatively charged, compose the atom"),
        "label": (("earth", "sun"), ("electrons", "nucleus")),
    },
    {
        "input": ("A singer expresses what he thinks by songs", 
                  "A programmer expresses what he thinks by writing code"),
        "label": (("singer", "songs"), ("programmer", "code")),
    },
    {
        "input": ("A road is where cars are", 
                  "boats sail on the lake to get from place to place"),
        "label": (("cars", "road"), ("boats", "lake")),
    },
    {
        "input": ("In order to prevent illness, we use medicine", 
                  "law is used to suppress anarchy"),
        "label": (("medicine", "illness"), ("law", "anarchy")),
    },
    {
        "input": ("His brain is full of thoughts", 
                  "The astronaut is hovering in space"),
        "label": (("thoughts", "brain"), ("astronaut", "space")),
    },
    {
        "input": ("The plant manages to survive in the desert even though it does not have much water", 
                  "The cat wanders the street and eats cans in order to survive"),
        "label": (("plant", "desert"), ("cat", "street")),
    },
    {
        "input": ("sunscreen protect our skin from the sun", 
                  "umbrella protect our body from the rain"),
        "label": (("sunscreen", "sun"), ("umbrella", "rain")),
    },
    {
        "input": ("we use air conditioner in the summer", 
                  "we use heater in the winter"),
        "label": (("air conditioner", "summer"), ("heater", "winter")),
    },
    {
        "input": ("student should do homework for practice", 
                  "civizen has duties such as tax or army"),
        "label": (("student", "homework"), ("civizen", "duties")),
    },
]

