import React, {useState, useEffect} from 'react'

import { useLocation } from 'react-router-dom'

import './TwoEntities.css'

const TwoEntities = () => {

    let location = useLocation()

    const [firstDirection, setFirstDirection] = useState({quasimodo: "", concept_net: "", google_autosuggest: ""})
    const [secondDirection, setSecondDirection] = useState({quasimodo: "", concept_net: "", google_autosuggest: ""})
    const [entity1, setEntity1] = useState("")
    const [entity2, setEntity2] = useState("")

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        let entity1 = params.get('entity1')
        let entity2 = params.get('entity2')
        setEntity1(entity1)
        setEntity2(entity2)
        fetch('/two-entities?' + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            setFirstDirection(data[`${entity1} .* ${entity2}`])
            setSecondDirection(data[`${entity2} .* ${entity1}`])
        })
      },[location.search])


    return (
    <div className="two-entities-container">
        <div style={{marginRight: '20px'}}>
            <table style={{width: '100%'}}>
                <tbody>
                    <tr>
                        <td className="direction-title">
                            {entity1} .* {entity2}
                        </td>
                    </tr>
                </tbody>
            </table>
            <table style={{width: '100%'}}>
                <tbody>
                    <tr>
                        <td className="content taken-from">
                            Taken from
                        </td>
                        <td className="content relations">
                            Relations
                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            Quasimodo
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.quasimodo}}>
                    
                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            Google
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.google_autosuggest}}>

                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            ConceptNet
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.concept_net}}>

                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div style={{marginLeft: '20px'}}>
            <table style={{width: '100%'}}>
                <tbody>
                    <tr>
                        <td className="direction-title">
                            {entity2} .* {entity1}
                        </td>
                    </tr>
                </tbody>
            </table>
            <table style={{width: '100%'}}>
                <tbody>
                    <tr>
                        <td className="content taken-from">
                            Taken from
                        </td>
                        <td className="content relations">
                            Relations
                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            Quasimodo
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.quasimodo}}>
                    
                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            Google
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.google_autosuggest}}>

                        </td>
                    </tr>
                    <tr>
                        <td className="content">
                            ConceptNet
                        </td>
                        <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.concept_net}}>

                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    );
}

export default TwoEntities;
