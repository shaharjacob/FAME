export const IsEmpty = (obj) => {
    for (var elem in obj) {
        return false
    }
    return true
}

export const topSolutionsOptions = (n) => {
    let options = []
    for (let i = 0; i < n; i++){
        options.push({
            value: i+1, label: i+1
        })
    }
    return options
}

export const options = [
    { value: 'air conditioner', label: 'air conditioner' },
    { value: 'anarchy', label: 'anarchy' },
    { value: 'astronaut', label: 'astronaut' },
    { value: 'atmosphere', label: 'atmosphere' },
    { value: 'atom', label: 'atom' },    
    { value: 'boats', label: 'boats' },
    { value: 'body', label: 'body' },
    { value: 'brain', label: 'brain' },
    { value: 'cans', label: 'cans' },
    { value: 'cars', label: 'cars' },
    { value: 'cat', label: 'cat' },
    { value: 'citizen', label: 'citizen' },
    { value: 'code', label: 'code' },
    { value: 'desert', label: 'desert' },
    { value: 'duties', label: 'duties' },
    { value: 'earth', label: 'earth' },
    { value: 'electrons', label: 'electrons' },
    { value: 'heater', label: 'heater' },
    { value: 'homework', label: 'homework' },
    { value: 'illness', label: 'illness' },
    { value: 'lake', label: 'lake' },
    { value: 'law', label: 'law' },
    { value: 'medicine', label: 'medicine' },
    { value: 'nucleus', label: 'nucleus' },
    { value: 'order', label: 'order' },
    { value: 'place', label: 'place' },
    { value: 'plant', label: 'plant' },
    { value: 'programmer', label: 'programmer' },
    { value: 'rain', label: 'rain' },
    { value: 'road', label: 'road' },
    { value: 'singer', label: 'singer' },
    { value: 'skin', label: 'skin' },
    { value: 'songs', label: 'songs' },
    { value: 'space', label: 'space' },
    { value: 'street', label: 'street' },
    { value: 'student', label: 'student' },
    { value: 'summer', label: 'summer' },
    { value: 'sun', label: 'sun' },
    { value: 'sunscreen', label: 'sunscreen' },
    { value: 'thoughts', label: 'thoughts' },
    { value: 'umbrella', label: 'umbrella' },
    { value: 'water', label: 'water' },
    { value: 'winter', label: 'winter' },  
];