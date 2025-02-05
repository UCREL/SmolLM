const fs = require( 'fs' );
const process = require( 'process' );
const express = require( 'express' );
const helmet = require( 'helmet' );
const rateLimit = require( 'express-rate-limit' );
const { crc16xmodem } = require( 'crc' )

const app = express();
const port = 8888;

const ENV_PROMPT_FILE = process.env.PROMPT_FILE || "data/example.json";
const ENV_STORAGE_PATH = process.env.STORAGE_PATH || "data/output/";

const PROMPTS = JSON.parse( fs.readFileSync( ENV_PROMPT_FILE, 'utf8' ) );

// Basic security headers
app.use( helmet() );

// Parse JSON body messages
app.use( express.json() );

// Rate limiting
app.use( rateLimit({
	windowMs: 15 * 60 * 1000, // 15 minutes
	limit: 100, // Limit each IP to 100 requests per `window` (here, per 15 minutes).
	standardHeaders: 'draft-7', // draft-6: `RateLimit-*` headers; draft-7: combined `RateLimit` header
	legacyHeaders: false // Disable the `X-RateLimit-*` headers.
}) );

app.set( "trust proxy", 2 ); /* number of proxies between user and server */

app.use( (req, res, next) => {
  console.log( `${req.method}: ${req.path}` )
  return next();
} );

app.get( '/', (_, res) => res.send( 'ok' ) );
app.get( '/v1/prompt/random', (req, res) => {
  const index = Math.floor( Math.random() * PROMPTS.length );
  const entry = PROMPTS[index];
  entry._index = index;

  res.json( entry );
} );

app.post( '/v1/prompt/vote', (req, res) => {
  const data = req.body;

  // console.log( data );

  if( data.index != PROMPTS[data.index]._index )
    console.warn( `Caution! Index mismatch (broken prompts list?). Saving anyway, but check your data!` );

  // Hard decouple the JSON!
  const entry = JSON.parse(JSON.stringify(PROMPTS[data.index]));
  entry.value = data.value;
  entry.vote_language = data.language;

  if( !validate_uid( data.user ) ) {
    console.warn( `Bad data from user: ${data.user}` );
    entry.user = data.user;
    data.user = '0000-0000';
  }

  console.log( `Writing to... ${ENV_STORAGE_PATH}/${data.user}.jslog` )
  fs.writeFileSync( `${ENV_STORAGE_PATH}/${data.user}.jslog`, `${JSON.stringify(entry)}\n`, { encoding: "utf8", flag: 'a', flush: true } );
  
  res.send( "ok" );
} );

function validate_uid( uid ) {
  const parts = uid.split("-");
  const crc = crc16xmodem( `${parts[0]}` ).toString(16).padStart(4,'0');

  console.log( `User ID Validation: ${uid} => ${parts[0]}-${parts[1]} crc ${crc}` );

  return parts[1] == crc;
}

app.get( '/v1/uid/generate', (req, res) => {
  const genMax = Math.min( req.query.max || 10, 9999 ) ;

  const userIDs = {};
  while( Object.keys(userIDs).length < genMax ) {
    const user_id = `${ Math.floor(Math.random()*9999) }`.padStart(4,'0');
    const crc = crc16xmodem( `${user_id}` ).toString(16).padStart(4,'0');
  
    const validKey = `${user_id}-${crc}`
    userIDs[validKey] = true;
  }

  res.send( Object.keys(userIDs).join("\n") );
} );

const server = app.listen( port, () => {
  console.log( `Example app listening on port ${port}` );
} );

process.on('SIGINT', () => {
  console.info( "Interrupted, shutting down." )
  server.close();
  process.exit( 0 )
})