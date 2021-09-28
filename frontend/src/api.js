import axios from "axios";


const baseURL = 'http://127.0.0.1:8000/api/v1';

export const axiosInstance = axios.create({
    baseURL: baseURL,
    timeout: 5000,
    headers: {
        Authorization: localStorage.getItem('access_token')
            ? 'Bearer ' + localStorage.getItem('access_token')
            : null,
        'Content-Type': 'application/json',
        accept: 'application/json',
    },
});


axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        const {
            config,
            response: { status },
        } = error;

        const originalRequest = config;
        console.log('실행!')

        if (status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            axios({
                method: 'post',
                url: `${baseURL}/accounts/token/refresh/`,
                data: { refresh: refreshToken },
            }).then((response) => {
                const accessTokens = response.data.access;


                localStorage.setItem('access_token', accessTokens);

                originalRequest.headers = { 'Authorization': 'Bearer ' + accessTokens };
                return axios(originalRequest);
            });
        }
        return Promise.reject(error);
    },
);

export default axiosInstance;
