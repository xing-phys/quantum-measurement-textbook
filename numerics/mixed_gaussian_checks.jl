# Standard-library demonstrations for Chapters 9 and 13.
# Run: julia numerics/mixed_gaussian_checks.jl
using LinearAlgebra, Random, Printf
const I2 = Matrix{ComplexF64}(I, 2, 2)
const X = ComplexF64[0 1; 1 0]
const Z = ComplexF64[1 0; 0 -1]
function localop(A, i, L)
    reduce(kron, [j == i ? A : I2 for j in 1:L])
end
sqrtpsd(A) = let E = eigen(Hermitian((A + A') / 2))
    E.vectors * Diagonal(sqrt.(max.(E.values, 0))) * E.vectors'
end
rootfidelity(rho, sigma) = clamp(real(tr(sqrtpsd(sqrtpsd(rho) * sigma * sqrtpsd(rho)))), 0, 1)

function main()
    # An exact state prepared by depth-two strongly symmetric pair dephasing.
    L = 5
    plus = ComplexF64[1, 1] / sqrt(2)
    psi = reduce(kron, fill(plus, L))
    rho = psi * psi'
    for i in 1:L-1
        W = localop(Z, i, L) * localop(Z, i+1, L)
        rho = (rho + W * rho * W') / 2
    end
    Gparity = reduce(kron, fill(X, L))
    target = (Matrix{ComplexF64}(I, 2^L, 2^L) + Gparity) / 2^L
    @assert norm(rho - target) < 1e-12
    @assert norm(Gparity * rho - rho) < 1e-12
    println("Parity-projected mixed state, L = ", L)
    println("distance,ordinary_ZZ,root_fidelity,renyi2")
    for j in 2:L
        W = localop(Z, 1, L) * localop(Z, j, L)
        sigma = W * rho * W'
        linear = real(tr(rho * W))
        f = rootfidelity(rho, sigma)
        r2 = real(tr(rho * sigma) / tr(rho * rho))
        @assert abs(linear) < 1e-12 && abs(f - 1) < 1e-7 && abs(r2 - 1) < 1e-12
        @printf("%d,%.8f,%.8f,%.8f\n", j-1, linear, f, r2)
    end
    
    # Gaussian trajectory update: G_ij = <c_j^dagger c_i>.
    function measure_site!(G, site, rng)
        p = clamp(real(G[site, site]), 0, 1)
        occupied = rand(rng) < p
        v = copy(G[:, site])
        if occupied
            G .-= (v * v') / p
        else
            G .+= (v * v') / (1-p)
        end
        G[:, site] .= 0
        G[site, :] .= 0
        G[site, site] = occupied ? 1 : 0
        occupied
    end
    rng = MersenneTwister(21461)
    L = 8
    h = zeros(ComplexF64, L, L)
    for i in 1:L-1
        h[i, i+1] = h[i+1, i] = -1
    end
    U = exp(-0.31im * h)
    G = Matrix(Diagonal(ComplexF64[isodd(i) ? 1 : 0 for i in 1:L]))
    for step in 1:100
        G = U * G * U'
        measure_site!(G, rand(rng, 1:L), rng)
        @assert norm(G-G') < 1e-10
        @assert norm(G*G-G) < 1e-10
        @assert abs(real(tr(G)) - L/2) < 1e-10
        @assert minimum(eigvals(Hermitian(G))) > -1e-10
        @assert maximum(eigvals(Hermitian(G))) < 1+1e-10
    end
    println("Gaussian update: 100 seeded steps passed Hermiticity, idempotency, spectrum, and charge checks.")
end
main()
