import axios from 'axios';
import { atom, selector } from 'recoil';
import { REACT_BACKEND_URL } from 'utils/url';

export const GetProduct = async () => {
    //const setProduct = useSetRecoilState(productState);
    try {
        const {
            data: { results }
        } = await axios.get(`${REACT_BACKEND_URL}/api/v1/products/list`);
        //setProduct({product: results});
        
        return results;
    } catch (e) {
        console.warn(e);
        return [];
    }
}


export const productState = atom({
    key: 'product',
    default: {
        product: []
    }
});


export const categoryState = atom({
    key: 'productCategory',
    default: "",
  });


export const productListSelector = selector({
    key: 'productList',
    get: async ({ get }) => {
        try {
            const category = get(categoryState);
            const {
                data
            } = await axios.get(`${REACT_BACKEND_URL}/api/v1/products/list?category=${category}`);

            return data;
        } catch (e) {
            console.warn(e);
            return [];
        }
    },
});


export const productQueryState = atom({
    key: 'productQuery',
    default: "",
  });

export const productSearchSelector = selector({
    key: 'productSearch',
    get: async ({ get }) => {
        try {
            const search = get(productQueryState);
            const {
                data
            } = await axios.get(`${REACT_BACKEND_URL}/api/v1/products/search?query=${search}`);
            return data;
        } catch (e) {
            console.warn(e);
            return [];
        }
    },
});