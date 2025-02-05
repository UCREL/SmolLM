import LocalizedStrings from 'react-localization';
import translations from '../data/translatons.json';
import { useState } from 'react';

let strings = new LocalizedStrings( translations );

export default function LoginWidget( props ) {
  const [proxy,setProxy] = useState( props.bindTo[0] );

  const _callback = props.bindTo[1];
  const _show = props.show || false;

  if( _show )
    showModal();

  strings.setLanguage( props.lang || "en" );

  //{/* Open the modal using document.getElementById('ID').showModal() method */}

  function showModal() {
    document.getElementById('loginModal').showModal()
  }

  function hideModel() {
    _callback( proxy );
    document.getElementById('loginModal').close()
  }

  function resetAndHide() {
    setProxy( '0000-0000' );
    _callback( '0000-0000' );
    document.getElementById('loginModal').close()
  }

  function handleReturnKey(e) {
    if( e.code == "Enter" ) {
      _callback( proxy );
      document.getElementById('loginModal').close()
    }
  }

  function handleInputChange(e) {
    let value = e.target.value.replace( /[^0-9a-f]/, "" );

    if( value.length > 4 ) {
      let parts = value.match( /([0-9a-f]{4})-?([0-9a-f]{0,4})/ );
      if( parts != null ) {
        parts.shift();
        value = parts.join( '-' );
      }
    }

    setProxy( value );
  };

  function genModalButton() {
    if( proxy == null || proxy.match( /([0-9a-f]{4})-?([0-9a-f]{0,4})/ ) == null || proxy.length != 9 || proxy == "0000-0000" )
      return <button className="btn btn-outline" onClick={()=>showModal()}>{strings.studyIdRequest}</button>;
    return <button className="btn btn-warning" onClick={()=>showModal()}>{strings.studyIdChange}</button>
  }

  return <div className='mt-5'>
    { genModalButton() }

    <dialog id="loginModal" className="modal modal-bottom sm:modal-middle">
      <div className="modal-box flex flex-col gap-3 border border-white">
        <h3 className="font-bold text-lg">{strings.loginTitle}</h3>
        
        <p className="py-4">{strings.loginBody}</p>
        
        <div className="join ml-auto mr-auto">
          <input
            className="input input-bordered join-item user-id-input"
            onChange={handleInputChange}
            onKeyUp={handleReturnKey}
            value={proxy || ""}
            placeholder='0000-0000' />
          <button className="btn join-item input-bordered btn-primary" onClick={() => hideModel()}>{strings.loginButton}</button>
        </div>

        <p>{strings.loginAlternative}</p>

        <form method="dialog">
          <button className="btn btn-outline" onClick={() => resetAndHide()}>{strings.loginCancelButton}</button>
        </form>
      </div>
    </dialog>
  </div>;
}