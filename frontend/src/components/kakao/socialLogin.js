
const CLIENT_ID = process.env.REACT_APP_KAKAO_CLIENT_ID
const REDIRECT_URI =  "http://localhost:3000/accounts/login/kakao/callback";
export const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code`;
