import React, {useState, useEffect} from 'react'

import { useLocation } from 'react-router-dom'
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './TwoEntities.css'
import GoogleLogo from '../../assets/google.png'
import QuasimodoLogo from '../../assets/quasimodo.png'
import ConceptnetLogo from '../../assets/conceptnet.png'
import OpenIELogo from '../../assets/openie.jpg'
import GPT3Logo from '../../assets/gpt3.png'

const TwoEntities = () => {

    let location = useLocation()

    const [firstDirection, setFirstDirection] = useState({quasimodo: "", concept_net: "", google_autosuggest: "", openie: "", gpt3: ""})
    const [secondDirection, setSecondDirection] = useState({quasimodo: "", concept_net: "", google_autosuggest: "", openie: "", gpt3: ""})
    const [entity1, setEntity1] = useState("")
    const [entity2, setEntity2] = useState("")
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        let entity1 = params.get('entity1')
        let entity2 = params.get('entity2')
        setEntity1(entity1)
        setEntity2(entity2)

        let prefix = ""
        if (process.env.NODE_ENV === "production") {
            prefix = "http://localhost:5031"
        }
        fetch(`${prefix}/api/two-entities?` + params)
        .then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            setFirstDirection(data[`${entity1} .* ${entity2}`])
            setSecondDirection(data[`${entity2} .* ${entity1}`])
            setIsLoading(false)
        })
      },[location.search])


    return (
    <>
        {isLoading
            ?
            <div className="overlay-loading">
                <LoadingOverlay
                    active={isLoading}
                    spinner={<ClipLoader size={70} color="#469cac" />}
                />
            </div>
            :
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
                                    <img className="resource-logo" src={QuasimodoLogo} alg="quasimodo" /><br/>
                                    <span style={{fontSize: '10px'}}>Quasimodo</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.quasimodo}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={GoogleLogo} alg="google" /><br/>
                                    <span style={{fontSize: '10px'}}>Google</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.google_autosuggest}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={OpenIELogo} alg="google" /><br/>
                                    <span style={{fontSize: '10px'}}>OpenIE</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.openie}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={GPT3Logo} alg="gpt3" /><br/>
                                    <span style={{fontSize: '10px'}}>GPT3</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.gpt3}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={ConceptnetLogo} alg="conceptnet" /><br/>
                                    <span style={{fontSize: '10px'}}>ConceptNet</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: firstDirection.concept_net}}></td>
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
                                    <img className="resource-logo" src={QuasimodoLogo} alg="quasimodo" /><br/>
                                    <span style={{fontSize: '10px'}}>Quasimodo</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.quasimodo}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={GoogleLogo} alg="google" /><br/>
                                    <span style={{fontSize: '10px'}}>Google</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.google_autosuggest}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={OpenIELogo} alg="google" /><br/>
                                    <span style={{fontSize: '10px'}}>OpenIE</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.openie}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={GPT3Logo} alg="gpt3" /><br/>
                                    <span style={{fontSize: '10px'}}>GPT3</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.gpt3}}></td>
                            </tr>
                            <tr>
                                <td className="content">
                                    <img className="resource-logo" src={ConceptnetLogo} alg="conceptnet" /><br/>
                                    <span style={{fontSize: '10px'}}>ConceptNet</span>
                                </td>
                                <td className="content props" dangerouslySetInnerHTML={{__html: secondDirection.concept_net}}></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        }
    </>
    );
}

export default TwoEntities;
