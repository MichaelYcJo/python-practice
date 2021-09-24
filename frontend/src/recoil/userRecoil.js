import { atom, selector } from 'recoil';


export const userState = atom({
    key: 'users',
    default: {
        isLoggedIn: false,
        token: null
    }
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