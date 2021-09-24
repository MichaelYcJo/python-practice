import { atom, selector } from 'recoil';

export const getToken = () => {
    const token = localStorage.getItem('token');
    const isLoggedIn = !!token;

    return {
        token,
        isLoggedIn,
    }
}


export const userState = atom({
    key: 'users',
    default: getToken()
});

/*
export const userLoginState = selector({
    key: 'countTitleState',
    get: ({ get }) => {
        return `현재 저장된 값은 ${get(userState)}`;
    },
    set: ({ set }, token) => { // 2번째 파라미터 에는 추가로 받을 인자
        console.log('setSelector Test')
        set(userState, token); // setter에 token 삽입
    },
});
*/