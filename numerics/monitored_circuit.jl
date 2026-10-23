#!/usr/bin/env julia
# Standard-library-only exact state-vector simulation. Julia 1.12.
using LinearAlgebra, Random, Statistics, DelimitedFiles
BLAS.set_num_threads(1)
const ROOT = normpath(joinpath(@__DIR__, ".."))

function haar4(rng)
    z = (randn(rng,4,4) + im*randn(rng,4,4))/sqrt(2)
    f = qr(z)
    Matrix(f.Q) * Diagonal(diag(f.R) ./ abs.(diag(f.R)))
end

# Sites numbered 0:L-1; site 0 is the least significant bit.
function gate!(psi, U, site)
    a, b = 1 << site, 1 << (site+1)
    for base in 0:length(psi)-1
        if (base & a == 0) && (base & b == 0)
            ids = (base+1, base+a+1, base+b+1, base+a+b+1)
            x = (psi[ids[1]],psi[ids[2]],psi[ids[3]],psi[ids[4]])
            for row in 1:4
                psi[ids[row]] = sum(U[row,col]*x[col] for col in 1:4)
            end
        end
    end
    psi
end

function measure!(psi, site, rng)
    mask = 1 << site
    p1 = sum(abs2(psi[i+1]) for i in 0:length(psi)-1 if i & mask != 0)
    p1 = clamp(p1,0.0,1.0)
    out = rand(rng) < p1
    prob = out ? p1 : 1-p1
    @assert prob > 0
    fac = inv(sqrt(prob))
    for i in 0:length(psi)-1
        psi[i+1] = ((i & mask != 0) == out) ? psi[i+1]*fac : 0
    end
    Int(out)
end

function entropy(psi,L; cut=L÷2)
    lam = abs2.(svdvals(reshape(psi,1<<cut,:)))
    -sum(x*log(x) for x in lam if x > 1e-15)
end

function trajectory(L,p,T,rng)
    psi = zeros(ComplexF64,1<<L); psi[1]=1
    values = Float64[0.0]
    # A time step is TWO brickwork layers followed by one measurement layer.
    for t in 1:T
        for offset in 0:1
            for site in offset:2:L-2
                gate!(psi,haar4(rng),site)
            end
        end
        for site in 0:L-1
            rand(rng)<p && measure!(psi,site,rng)
        end
        @assert abs(sum(abs2,psi)-1)<1e-10
        t%2 == 0 && push!(values,entropy(psi,L))
    end
    values
end

function validate()
    rng = MersenneTwister(41)
    for _ in 1:12
        U=haar4(rng)
        @assert norm(U'*U-I)<1e-12
    end
    bell = ComplexF64[1,0,0,1]/sqrt(2)
    @assert abs(entropy(bell,2)-log(2))<1e-12
    prod = ComplexF64[1,0,0,0]
    @assert abs(entropy(prod,2))<1e-12
    @assert abs(sum(abs2,gate!(copy(bell),haar4(rng),0))-1)<1e-12
    @assert maximum(abs.(trajectory(6,1.0,8,rng)))<1e-10
    # Statistical Born-rule check, independent fresh Bell states.
    freq = mean(measure!(copy(bell),0,rng) for _ in 1:4000)
    @assert abs(freq-0.5)<0.04
    println("Validation passed: Haar unitarity, norm, Bell/product entropy, p=1, Born sampling.")
end

function main()
    validate()
    mkpath(joinpath(ROOT,"assets","data"))
    T, N = 60, 64
    ps = [0.0,0.1,0.2,0.4,0.8,1.0]
    rows = Any["L" "p" "t" "mean_entropy_nats" "standard_error" "trajectories"]
    for L in [6,8,10], (pi,p) in enumerate(ps)
        rng=MersenneTwister(20261023 + L*1000 + pi)
        vals=hcat([trajectory(L,p,T,rng) for _ in 1:N]...)
        for j in axes(vals,1)
            rows=vcat(rows,Any[L p 2*(j-1) mean(vals[j,:]) std(vals[j,:])/sqrt(N) N])
        end
        println("Completed L=$L p=$p")
    end
    writedlm(joinpath(ROOT,"assets","data","circuit_entropy.csv"),rows,',')
end

if abspath(PROGRAM_FILE)==@__FILE__
    "--validate" in ARGS ? validate() : main()
end
