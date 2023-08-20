import { LoginAxiosInstance } from 'api';
import { atom, selector } from 'recoil';


export const orderState = atom({
    key: "orderState",
    default: null,
});

export const orderListSelector = selector({
    key: 'orderList',
    get: async ({ get }) => {
        get(orderState);
        try {
            const { status, data } = await LoginAxiosInstance.get(
                '/orders/list');
            if (status === 200) {
                return data;
            }
        }catch(e) {
            console.warn(e);
            return [];
        }
    },
    set({ set }, newValue) {
        set(orderListSelector, newValue);
    }
});