import api from '../api';
import { jwtDecode } from "jwt-decode";
import { ACCESS_TOKEN } from "../constants";

export const formatDate = (dateString) => {
    const date = new Date(dateString);

    const optionsDate = { year: 'numeric', month: '2-digit', day: '2-digit' };
    const optionsTime = { hour: '2-digit', minute: '2-digit' };

    const formattedDate = date.toLocaleDateString('de-DE', optionsDate);
    const formattedTime = date.toLocaleTimeString('de-DE', optionsTime);

    return `${formattedDate} ${formattedTime}`;
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
};

export const getRequest = async (url, setIsLoading) => {
    setIsLoading(true);

    try {
        const response = await api.get(url);
        return response.data;
    } catch (e) {
        throw new Error(e.message);
    } finally {
        setIsLoading(false);
    }
};

export const isAdmin = () => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
        try {
            const decodedToken = jwtDecode(token);
            return decodedToken.is_staff;
        } catch (error) {
            console.error("Fehler beim Dekodieren des Tokens:", error);
            return false;
        }
    }
    return false;
};
