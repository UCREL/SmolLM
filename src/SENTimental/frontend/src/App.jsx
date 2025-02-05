import { createContext, useContext, useEffect, useState } from 'react'
import './App.css'
import translations from './data/translatons.json';
import LocalizedStrings from 'react-localization';
import LoginWidget from './components/LoginWidget';
import { SliderComponent } from './components/SliderComponent';

let strings = new LocalizedStrings( translations );

function App() {
  const [language, setLanguage] = useState( "cy" );
  const [userId, setUserId] = useState( null );
  const [showLoginModal, setShowLoginModal] = useState( false );

  const [welsh, setWelsh] = useState( "..." );
  const [english, setEnglish] = useState( "..." );
  const [sentiment, setSentiment] = useState( { positive: 0, negative: 0, neutral: 0, score: 0 } );
  const [userSentiment, setUserSentiment] = useState( 0 );
  const [index, setIndex] = useState( -1 );

  useEffect( () => {
    const stored_uid = localStorage.getItem( 'study_key' ) || '0000-0000';

    localStorage.setItem( 'study_key', stored_uid );

    setUserId( stored_uid )
  }, [userId] )

  function dumpStorage() {
    const data = {}
    for( let i=0; i<localStorage.length; i++ ) {
      const key = localStorage.key(i);
      const value = localStorage.getItem( key );

      data[key] = value;
    }
    return data;
  }

  function getPrompt() {
    fetch( "/v1/prompt/random" )
    .then( res => res.json() )
    .then( (json) => {
      setWelsh( json.cy );
      setEnglish( json.en );
      setSentiment( {
        positive: json.positive,
        negative: json.negative,
        neutral: json.neutral,
        score: json.score
      } );
      setIndex( json._index );
    } );
  }

  function checkLogin() {
    if( userId == null ) {
      setShowLoginModal( true );
      return false;
    }
    
    if( !validateUserId() ) {
      return false;
    }

    return true;
  }

  function vote( index, state ) {
    fetch(
      '/v1/prompt/vote',
      {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify( {
          "index": index,
          "value": state,
          "user": userId,
          "language": language
        } )
      }
    );
  }

  /*function upVote() {
    checkLogin()
    vote( index, 1 );
    getPrompt();
  }

  function downVote() {
    checkLogin()
    vote( index, -1 );
    getPrompt();
  }*/

  function valueVote() {
    checkLogin()
    vote( index, userSentiment / 100.0 );
    setUserSentiment( 50 );
    getPrompt();
  }

  function skipVote() {
    setUserSentiment( 50 );
    getPrompt();
  }

  useEffect( () => {
    setUserSentiment( 50 );
    getPrompt();
  }, [] );

  function humanizeScore( score ) {
    if( score < -25 ) {
      return <strong className='text-3xl'>{strings.stronglyNegative}</strong>
    }
    if( score < -10 ) {
      return <strong className='text-3xl'>{strings.slightlyNegative}</strong>
    }
    if( score > 25 ) {
      return <strong className='text-3xl'>{strings.stronglyPositive}</strong>
    }
    if( score > 10 ) {
      return <strong className='text-3xl'>{strings.slightlyPositive}</strong>
    }

    return <strong className='text-3xl'>{strings.neutral}</strong>
  }

  function validateUserId() {
    const valid = userId && userId.length == 9 && userId.match( /^[0-9a-f]{4}-[0-9a-f]{4}$/ );

    if( valid )
      localStorage.setItem( "study_key", userId );

    return valid;
  }

  function userIdentBar() {
    if( !validateUserId() || userId == '0000-0000' )
      return <div className='bg-red-900 text-white font-bold'>{strings.missingStudyId}</div>;

    return <div className='font-bold'>{strings.studyIdPrefix} {userId}</div>
  }

  strings.setLanguage( language );

  let message = welsh;
  if( language === "en" )
    message = english;

  const loginModal = <LoginWidget lang={language} show={showLoginModal} bindTo={[userId,setUserId]} />;

  const footerBlock = {
    "en": <div className='mt-10 rounded-lg border border-gray-700'>
      <p>Created by <a className="underline" href="https://johnvidler.co.uk" target='_blank'>John Vidler</a> for the SmolLM project as part of the <a className="underline" href="https://ucrel.lancs.ac.uk/" target='_blank'>UCREL</a> research group at the <a className="underline" href="https://www.lancaster.ac.uk/scc/" target='_blank'>School of Computing and Communications, Lancaster University</a></p>
      <p>A web cookie is used to store the user's Study ID to retain it between sessions.</p>
    </div>,
    "cy": <div className='mt-10 rounded-lg border border-gray-700'>
      <p>Crëwyd gan <a className="underline" href="https://johnvidler.co.uk" target='_blank'>John Vidler</a> ar gyfer prosiect SmolLM fel rhan o grŵp ymchwil <a className="underline" href="https://ucrel.lancs.ac.uk/" target='_blank'>UCREL</a> yn <a className="underline" href="https://www.lancaster.ac.uk/scc/" target='_blank'>Ysgol Cyfrifiadura a Chyfathrebu, Prifysgol Caerhirfryn</a></p>
      <p>Defnyddir cwci gwe i storio ID Astudio'r defnyddiwr i'w gadw rhwng sesiynau.</p>
    </div> }[language];

  const colorBands = [
    { bound: 0, color: "blue" },
    { bound: 40, color: "white" },
    { bound: 70, color: "red" },
  ];

  return (
    <div className='flex flex-col'>
      <div className="mb-20">
        <h1>{strings.title}</h1>
        <div>{userIdentBar()}</div>
        {loginModal}
      </div>

      <div>
        <div className="join">
          <input className="join-item btn btn-sm" type="radio" name="userLangSelect" aria-label="Cymraeg" defaultChecked={language === 'cy'} onClick={ () => setLanguage('cy') } />
          <input className="join-item btn btn-sm" type="radio" name="userLangSelect" aria-label="English" defaultChecked={language === 'en'} onClick={ () => setLanguage('en') } />
        </div>
        
        <div className='mt-10 ml-auto mr-auto flex flex-col gap-3 place-items-center'>
          <p>{strings.sampleTextPrefix}</p>
        </div>

        <div className='mt-10 text-4xl border-2 rounded-3xl border-gray-700 bg-gray-700 p-5 italic'>
          <div className='text-left inline-block mr-auto ml-auto quotetext'>{message}</div>
        </div>

        <div className='mt-10 ml-auto mr-auto flex flex-col gap-3 place-items-center'>
          <p>{ strings.userScoreStatement }</p>
          <div>{ humanizeScore(userSentiment-50) }</div>
        
          <SliderComponent min={0} max={100} bindTo={[userSentiment,setUserSentiment]} step={10} thresholds={colorBands} />

          <button className='btn btn-primary max-w-sm min-w-48' onClick={() => valueVote()}>{strings.submit}</button>
          <div>or</div>
          <button className='btn btn-secondary btn-outline max-w-sm min-w-48' onClick={() => skipVote()}>{strings.skip}</button>
        </div>

      </div>
      {footerBlock}
      
    </div>
  )
}

export default App