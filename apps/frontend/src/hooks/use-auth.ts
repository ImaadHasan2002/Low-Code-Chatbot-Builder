// components/features/auth/hooks/useAuth.ts
import { useMutation } from '@tanstack/react-query'
import { authAPI } from '@/lib/api/endpoints/auth'
import { useRouter } from 'next/navigation'

export const useAuth = () => {
  const router = useRouter()
  
  const loginMutation = useMutation({
    mutationFn: authAPI.login,
    onSuccess: () => {
      router.push('/dashboard')
    }
  })

  const signupMutation = useMutation({
    mutationFn: authAPI.signup,
    onSuccess: () => router.push('/login?signup_success=true')
  })

  const logoutMutation = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      router.push('/login')
    }
  })

  return { loginMutation, signupMutation, logoutMutation }
}