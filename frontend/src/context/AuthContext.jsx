import {
    createContext
    , useContext
    , useState
    , useEffect
} from "react"

const AuthContext = createContext()

  export const useAuth = () =>{
    const context = useContext(AuthContext)
    if(!context){
        throw new Error ("useAuth debe usarse dentro de AuthProvider")
    }
    return context
}

export const AuthProvider = ( {children} ) => {
    const [user, setUser] = useState(null)
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [loading, setLoading] = useState(false)

    useEffect( () => {
        const savedUser = localStorage.getItem("user")
        const savedAuth = localStorage.getItem("isAuthenticated")

        if ( savedAuth && savedUser === "true" ){
            setUser( JSON.parse(savedUser) )
            setIsAuthenticated(true)
        }

        setLoading(false)
    } ,[])

   const login = (userData) => {
    setUser(userData)
    setIsAuthenticated(true)
    localStorage.setItem("user", JSON.stringify(userData))
    localStorage.setItem("isAuthenticated", "true")
}

const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem("user")
    localStorage.removeItem("isAuthenticated")
}

const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout
}

 return (
    <AuthContext.Provider value={value}>
        {children}
    </AuthContext.Provider>
)

}
